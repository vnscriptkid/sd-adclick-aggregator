from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, window
from pyspark.sql.window import Window
from pyspark.sql.functions import dense_rank
from pyspark.sql.types import StructType, StringType, TimestampType, StructField

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Read CSV from S3") \
    .config("spark.hadoop.fs.s3a.access.key", "xxx") \
    .config("spark.hadoop.fs.s3a.secret.key", "xxx") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .getOrCreate()

# Define schema
schema = StructType([
    StructField("ad_id", StringType(), True),
    StructField("click_timestamp", TimestampType(), True),
    StructField("user", StringType(), True),
    StructField("ip", StringType(), True),
    StructField("country", StringType(), True)
])

# Read CSV files as a stream
df = spark.readStream \
    .schema(schema) \
    .csv("s3a://bigdata-data-store/stream/")

# Apply watermarking and aggregation
aggregated_df = df \
    .groupBy(
        window(col("click_timestamp"), "2 minutes"), col("ad_id")
    ).agg(count("*").alias("click_count"))

# Order by window first and then click_count in descending order
ordered_df = aggregated_df.orderBy(col("window").asc(), col("click_count").desc())

# Write the results to console
query = ordered_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

# Wait for the streaming to finish
query.awaitTermination()

# Stop the Spark session (will only stop if you manually terminate the streaming)
spark.stop()

# +------------------------------------------+-----+-----------+
# |window                                    |ad_id|click_count|
# +------------------------------------------+-----+-----------+
# |{2024-08-09 00:00:00, 2024-08-09 00:02:00}|ad001|3          |
# |{2024-08-09 00:00:00, 2024-08-09 00:02:00}|ad002|1          |

# |{2024-08-09 00:02:00, 2024-08-09 00:04:00}|ad003|2          |
# |{2024-08-09 00:02:00, 2024-08-09 00:04:00}|ad001|1          |
# |{2024-08-09 00:02:00, 2024-08-09 00:04:00}|ad002|1          |
# +------------------------------------------+-----+-----------+