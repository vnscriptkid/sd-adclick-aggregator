package main

import (
	"fmt"
	"math/rand"
	"time"
)

// GeneratePartitionKey generates a partition key for a given AdId
func GeneratePartitionKey(adId string, numSubPartitions int) string {
	rand.Seed(time.Now().UnixNano())
	subPartition := rand.Intn(numSubPartitions)
	return fmt.Sprintf("%s:%d", adId, subPartition)
}

func main() {
	adId := "12345"
	numSubPartitions := 10

	// Simulate generating partition keys for clicks
	for i := 0; i < 20; i++ {
		partitionKey := GeneratePartitionKey(adId, numSubPartitions)
		fmt.Println("Partition Key:", partitionKey)
	}
}
