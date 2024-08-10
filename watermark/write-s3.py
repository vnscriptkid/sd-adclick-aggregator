from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Read CSV from S3") \
    .config("spark.hadoop.fs.s3a.access.key", "xxx") \
    .config("spark.hadoop.fs.s3a.secret.key", "xxx") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .getOrCreate()

data = [(i, f"data_{i}") for i in range(1000)]
df = spark.createDataFrame(data, ["id", "value"])

# Write DataFrame to Parquet in MinIO
df.write.mode("overwrite").option("maxRecordsPerFile", 100).parquet("s3a://bigdata-data-store/parquet-data")

# Show the DataFrame content
df.show()
