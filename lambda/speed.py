from kafka import KafkaConsumer, KafkaProducer
import json
import redis

# Initialize Kafka consumer for real-time clicks
consumer = KafkaConsumer('ad-clicks', bootstrap_servers='localhost:9092')

# Connect to Redis for storing real-time stats
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Process real-time clicks
for message in consumer:
    event = json.loads(message.value.decode('utf-8'))
    ad_id = event['ad_id']
    
    # Increment real-time click count in Redis
    redis_client.hincrby(f'ad:{ad_id}', 'click_count', 1)
    
    # Update real-time CTR or other metrics if needed
    # Additional logic for fraud detection could be added here
