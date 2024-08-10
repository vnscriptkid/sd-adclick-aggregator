from pyspark.sql import SparkSession
import redis

# Initialize Spark session
spark = SparkSession.builder.appName("AdClickBatchProcessing").getOrCreate()

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def process_batch_and_reset(ad_id, batch_cutoff_time):
    # Process the batch data (same as before)
    historical_clicks = spark.read.parquet("s3://ad-click-data/historical/")
    click_aggregates = historical_clicks.groupBy("ad_id").agg({
        "click_id": "count",
        "user_id": "approx_count_distinct"
    })
    
    # Store the result in your batch data store
    click_aggregates.write.mode("overwrite").parquet("s3://ad-click-data/aggregates/")
    
    # Reset real-time data in Redis after batch processing
    redis_client.hset(f'ad:{ad_id}', 'click_count_since_cutoff', 0)
    redis_client.hset(f'ad:{ad_id}', 'last_update', batch_cutoff_time.strftime('%Y-%m-%dT%H:%M:%SZ'))

# Example usage in a batch job
batch_cutoff_time = datetime(2024, 8, 10, 2, 0, 0)
process_batch_and_reset('ad_123', batch_cutoff_time)
