package main

import (
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/confluentinc/confluent-kafka-go/kafka"
)

// Impression represents a user impression event
type Impression struct {
	UserID    string `json:"user_id"`
	EventID   string `json:"event_id"`
	Timestamp string `json:"timestamp"`
}

// produceDummyData generates and sends dummy impressions to Kafka
func produceDummyData() {
	producer, err := kafka.NewProducer(&kafka.ConfigMap{"bootstrap.servers": "localhost:9092"})
	if err != nil {
		log.Fatalf("Failed to create producer: %s", err)
	}
	defer producer.Close()

	// Channel to handle delivery reports
	deliveryChan := make(chan kafka.Event)

	// Generate impressions for event1 from different users
	eventID := "event1"
	users := []string{"user1", "user2", "user3", "user4"}
	timestamps := []string{
		"2024-08-18T14:00:00Z",
		"2024-08-18T14:02:00Z",
		"2024-08-18T14:05:00Z",
		"2024-08-18T14:09:00Z",
	}

	for _, ts := range timestamps {
		for _, user := range users {
			impression := Impression{
				UserID:    user,
				EventID:   eventID,
				Timestamp: ts,
			}

			value, err := json.Marshal(impression)
			if err != nil {
				log.Printf("Error marshalling impression: %v", err)
				continue
			}

			topic := "impressions"
			// Produce the message with delivery report
			err = producer.Produce(&kafka.Message{
				TopicPartition: kafka.TopicPartition{
					Topic:     &topic,
					Partition: kafka.PartitionAny,
				},
				Value: value,
				Key:   []byte(eventID),
			}, deliveryChan)

			if err != nil {
				log.Printf("Failed to produce message: %v", err)
			}
		}
	}

	// Wait for delivery reports and handle them
	go func() {
		for e := range deliveryChan {
			switch ev := e.(type) {
			case *kafka.Message:
				if ev.TopicPartition.Error != nil {
					log.Printf("Failed to deliver message: %v\n", ev.TopicPartition)
				} else {
					log.Printf("Successfully delivered message to %v\n", ev.TopicPartition)
				}
			}
		}
	}()

	// Wait for all messages to be delivered
	producer.Flush(15 * 1000)
	close(deliveryChan)

	log.Println("Dummy data produced")
}

func main() {
	// Graceful shutdown handling
	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	go produceDummyData()

	<-sigchan
	log.Println("Shutting down producer")
}
