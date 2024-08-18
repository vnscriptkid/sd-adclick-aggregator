package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
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
	defer rdb.Close()

	// Example query to count unique users for event "event1" within a time range
	startTime, _ := time.Parse(time.RFC3339, "2024-08-18T14:00:00Z")
	endTime, _ := time.Parse(time.RFC3339, "2024-08-18T14:10:00Z")
	count := countUniqueUsersForEventInRange("event1", startTime, endTime)
	log.Printf("Unique users for event1 from 14:00 to 14:10: %d", count)

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
