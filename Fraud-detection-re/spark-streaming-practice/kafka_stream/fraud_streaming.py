# Set HADOOP_USER_NAME at the very top to bypass FSPermissionChecker
import os
os.environ['HADOOP_USER_NAME'] = 'root'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Create SparkSession with HDFS configuration for Windows 11
# Note: dfs.client.use.datanode.hostname=false is typically needed on Windows
# to avoid hostname resolution issues when DataNode is in Docker
spark = SparkSession.builder \
    .appName("FraudToHDFS") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .config("spark.hadoop.dfs.datanode.address", "127.0.0.1:9866") \
    .config("spark.hadoop.dfs.client.block.write.replace-datanode-on-failure.enabled", "false") \
    .getOrCreate()

# Set log level to reduce verbosity
spark.sparkContext.setLogLevel("WARN")

# Define schema for incoming Kafka messages
schema = StructType([
    StructField("user", StringType(), True),
    StructField("amount", IntegerType(), True),
    StructField("source", StringType(), True)
])

# Read stream from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transactions_partitioned") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON from Kafka messages
json_df = raw_df.selectExpr("CAST(value AS STRING) as value") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Add fraud detection flag
processed_df = json_df.withColumn("is_fraud", col("amount") > 500)

# Write stream 1: All transactions to /data/raw/transactions
query_all_transactions = processed_df.writeStream \
    .format("parquet") \
    .option("path", "hdfs://localhost:9000/data/raw/transactions") \
    .option("checkpointLocation", "hdfs://localhost:9000/checkpoints/all_transactions") \
    .outputMode("append") \
    .start()

# Write stream 2: Filtered fraud data to /data/processed/fraud
query_fraud = processed_df.filter(col("is_fraud") == True) \
    .writeStream \
    .format("parquet") \
    .option("path", "hdfs://localhost:9000/data/processed/fraud") \
    .option("checkpointLocation", "hdfs://localhost:9000/checkpoints/fraud_data") \
    .outputMode("append") \
    .start()

print("Streaming started. Writing all transactions to HDFS...")
print("- All transactions: hdfs://localhost:9000/data/raw/transactions")
print("- Fraud transactions: hdfs://localhost:9000/data/processed/fraud")

# Wait for any stream to terminate
spark.streams.awaitAnyTermination()