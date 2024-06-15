from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, split, expr

# Initialize Spark session
spark = SparkSession.builder \
    .appName("AdClickStreaming") \
    .getOrCreate()

# Read from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "your_kafka_bootstrap_servers") \
    .option("subscribe", "clicks") \
    .option("startingOffsets", "latest") \
    .load()

# Convert the binary value column to string
clicks_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Parse the partition key
# Split the value into adId and handle cases where the sub-partition might not be present
parsed_df = clicks_df.select(
    split(col("value"), ":").getItem(0).alias("adId"),
    expr("current_timestamp()").alias("timestamp")
)

# Aggregate clicks per minute for each ad
clicks_per_minute_df = parsed_df \
    .groupBy(
        window(col("timestamp"), "1 minute"),
        col("adId")
    ) \
    .count() \
    .select(
        col("window.start").alias("start_time"),
        col("adId"),
        col("count").alias("click_count")
    )

# Output the results to the console
query = clicks_per_minute_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .trigger(processingTime="1 minute") \
    .start()

query.awaitTermination()
