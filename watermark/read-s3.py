from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Read CSV from S3") \
    .config("spark.hadoop.fs.s3a.access.key", "xxx") \
    .config("spark.hadoop.fs.s3a.secret.key", "xxx") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
    .getOrCreate()

# Read CSV file from S3
df = spark.read.csv("s3a://bigdata-data-store/data.csv", header=True, inferSchema=True)

# Show the DataFrame content
df.show()
