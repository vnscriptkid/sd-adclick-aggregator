package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	"github.com/go-redis/redis/v8"
	"github.com/vnscriptkid/sd-adclick-aggregator/impression-counting-hyperloglog/model"
)

var (
	rdb *redis.Client
	ctx = context.Background()
)

func main() {
	// Initialize Redis client
	rdb = redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
		DB:   0, // use default DB
	})

	// Kafka consumer configuration
	consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers": "localhost:9092",
		"group.id":          "impression_counter",
		"auto.offset.reset": "earliest",
	})
	if err != nil {
		log.Fatalf("Failed to create consumer: %s", err)
	}

	// Subscribe to the Kafka topic
	err = consumer.Subscribe("impressions", nil)
	if err != nil {
		log.Fatalf("Failed to subscribe to topic: %s", err)
	}

	// Graceful shutdown handling
	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	fmt.Printf("Consumer started")
	run := true
	for run {
		select {
		case sig := <-sigchan:
			log.Printf("Caught signal %v: terminating", sig)
			run = false
		default:
			msg, err := consumer.ReadMessage(-1)
			fmt.Printf("Message received: %s\n", string(msg.Value))
			if err == nil {
				// Process the message and update the HyperLogLog in Redis
				processImpression(msg.Value)
			} else {
				// Log errors (optional: implement retry mechanism)
				log.Printf("Consumer error: %v (%v)\n", err, msg)
			}
		}
	}

	// Example query to count unique users for event "event1" within a time range
	startTime, _ := time.Parse(time.RFC3339, "2024-08-18T14:00:00Z")
	endTime, _ := time.Parse(time.RFC3339, "2024-08-18T14:10:00Z")
	count := countUniqueUsersForEventInRange("event1", startTime, endTime)
	log.Printf("Unique users for event1 from 14:00 to 14:10: %d", count)

	consumer.Close()
	rdb.Close()
}

// processImpression updates the HyperLogLog with impression data based on minute granularity
func processImpression(value []byte) {
	var impression model.Impression
	if err := json.Unmarshal(value, &impression); err != nil {
		log.Printf("Error unmarshalling JSON: %v", err)
		return
	}

	// Parse the timestamp and round to the nearest minute
	t, err := time.Parse(time.RFC3339, impression.Timestamp)
	if err != nil {
		log.Printf("Error parsing timestamp: %v", err)
		return
	}
	minuteKey := t.Format("2006-01-02T15:04")

	// Use the eventID and minuteKey as the Redis key
	key := fmt.Sprintf("impressions_hll:%s:%s", impression.EventID, minuteKey)

	// Add the impression to the HyperLogLog
	uniqueID := fmt.Sprintf("%s:%s", impression.UserID, impression.EventID)
	err = rdb.PFAdd(ctx, key, uniqueID).Err()
	if err != nil {
		log.Printf("Error updating HyperLogLog: %v", err)
	} else {
		log.Printf("Impression added: %s to %s", uniqueID, key)
	}
}

// countUniqueUsersForEventInRange counts the unique users who viewed a specific event within a time range
func countUniqueUsersForEventInRange(eventID string, startTime, endTime time.Time) int64 {
	// Collect all keys for the specified event in the time range
	var keys []string
	for t := startTime; !t.After(endTime); t = t.Add(time.Minute) {
		minuteKey := t.Format("2006-01-02T15:04")
		key := fmt.Sprintf("impressions_hll:%s:%s", eventID, minuteKey)
		keys = append(keys, key)
	}

	// Use PFCOUNT on the union of all these keys
	tempKey := fmt.Sprintf("temp_union:%s:%d", eventID, time.Now().UnixNano())
	err := rdb.PFMerge(ctx, tempKey, keys...).Err()
	if err != nil {
		log.Printf("Error merging HyperLogLogs: %v", err)
		return 0
	}
	defer rdb.Del(ctx, tempKey) // Clean up the temporary key

	count, err := rdb.PFCount(ctx, tempKey).Result()
	if err != nil {
		log.Printf("Error getting merged HyperLogLog count: %v", err)
		return 0
	}
	return count
}
