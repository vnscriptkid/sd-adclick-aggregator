from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd
from IPython.display import display, clear_output

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkStream") \
    .getOrCreate()

# Kafka configuration
kafka_bootstrap_servers = "cool-civet-11505-us1-kafka.upstash.io:9092"
kafka_sasl_mechanism = "SCRAM-SHA-256"
kafka_security_protocol = "SASL_SSL"
kafka_jaas_module = "org.apache.kafka.common.security.scram.ScramLoginModule"
kafka_sasl_username = "xxx"
kafka_sasl_password = "yyy"

df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("kafka.security.protocol", kafka_security_protocol) \
        .option("kafka.sasl.mechanism", kafka_sasl_mechanism) \
        .option("kafka.sasl.jaas.config", f"{kafka_jaas_module} required username='{kafka_sasl_username}' password='{kafka_sasl_password}';") \
        .option("startingOffsets", "earliest") \
        .option("subscribe", "clicks") \
        .load()

df.printSchema()

# Define schema for the value
schema = StructType([
    StructField("adsId", StringType(), True),
    StructField("createdAt", TimestampType(), True)
])

# Parse the value field to JSON
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Aggregate by adsId over a time window of 1 minute
aggregated_df = parsed_df \
    .withWatermark("createdAt", "1 minute") \
    .groupBy(
        window(col("createdAt"), "1 minute"),
        col("adsId")
    ) \
    .count() \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("adsId"),
        col("count").alias("total_clicks")
    )

def display_batch(batch_df, batch_id):
    # Collect the batch data to the driver as a Pandas DataFrame
    pandas_df = batch_df.toPandas()
    
    # Clear the previous output
    clear_output(wait=True)
    
    # Display the DataFrame
    display(pandas_df)

# Write the aggregated data to a foreachBatch function
query = aggregated_df \
    .writeStream \
    .outputMode("update") \
    .foreachBatch(display_batch) \
    .start()

# Wait for the termination of the query
query.awaitTermination()