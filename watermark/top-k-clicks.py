from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, window
from pyspark.sql.window import Window
from pyspark.sql.functions import dense_rank

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Read CSV from S3") \
    .config("spark.hadoop.fs.s3a.access.key", "xxx") \
    .config("spark.hadoop.fs.s3a.secret.key", "xxx") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .getOrCreate()

schema = "ad_id STRING, click_timestamp TIMESTAMP, user STRING, ip STRING, country STRING"

# Load CSV data
df = spark.read.csv("s3a://bigdata-data-store/clicks.csv", schema=schema, header=True)

# Perform aggregation to get click counts per minute per ad
aggregated_df = df.groupBy(
    window(col("click_timestamp"), "5 minute"), col("ad_id")
).agg(count("*").alias("click_count"))

# Find the Top N most clicked ads per minute
N = 2 # Top 2 most clicked ads
window_spec = Window.partitionBy("window").orderBy(col("click_count").desc())

top_n_df = aggregated_df.withColumn("rank", dense_rank().over(window_spec)).filter(col("rank") <= N)

# Show the results
top_n_df.show(truncate=False)

# Stop the Spark session
spark.stop()

# +------------------------------------------+-----+-----------+----+
# |window                                    |ad_id|click_count|rank|
# +------------------------------------------+-----+-----------+----+
# |{2024-08-09 00:00:00, 2024-08-09 00:05:00}|ad001|4          |1   |
# |{2024-08-09 00:00:00, 2024-08-09 00:05:00}|ad002|3          |2   |
# |{2024-08-09 00:00:00, 2024-08-09 00:05:00}|ad003|2          |3   |
# |{2024-08-09 00:05:00, 2024-08-09 00:10:00}|ad001|2          |1   |
# |{2024-08-09 00:05:00, 2024-08-09 00:10:00}|ad003|1          |2   |
# |{2024-08-09 00:05:00, 2024-08-09 00:10:00}|ad002|1          |2   |
# +------------------------------------------+-----+-----------+----+