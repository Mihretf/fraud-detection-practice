import os
# Set HADOOP_USER_NAME to root for HDFS permissions inside Docker
os.environ['HADOOP_USER_NAME'] = 'root'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StructField, StringType, FloatType, DoubleType, LongType

# 1. DOCKER-OPTIMIZED CONNECTION
spark = SparkSession.builder \
    .appName("FraudToHDFS") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. SCHEMAS
schema = StructType([
    StructField("user", StringType(), True),
    StructField("amount", FloatType(), True),
    StructField("source", StringType(), True),
    StructField("lat", FloatType(), True),
    StructField("lon", FloatType(), True),
    StructField("timestamp", FloatType(), True)
])

profile_schema = StructType([
    StructField("user", StringType(), True),
    StructField("avg_amount", DoubleType(), True),
    StructField("std_dev", DoubleType(), True),
    StructField("home_lat", DoubleType(), True),
    StructField("home_lon", DoubleType(), True),
    StructField("transaction_count", LongType(), True)
])

# 3. KAFKA SOURCE (Using service name: kafka_practice)
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka_practice:9092") \
    .option("subscribe", "transactions_partitioned") \
    .option("startingOffsets", "latest") \
    .load()

json_df = raw_df.selectExpr("CAST(value AS STRING) as value") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 4. LOAD PROFILES (Static Join from HDFS)
try:
    profiles_df = spark.read.schema(profile_schema).parquet("hdfs://namenode:9000/data/profiles/latest")
    print("SYSTEM: Profile 'Cheat Sheet' connected.")
except Exception:
    print("SYSTEM: Profile folder not found. Initializing with empty rules.")
    profiles_df = spark.createDataFrame([], profile_schema)

# 5. THE JOIN AND FRAUD LOGIC
enriched_df = json_df.join(profiles_df, on="user", how="left")

processed_df = enriched_df.withColumn(
    "is_fraud", 
    when(col("avg_amount").isNull(), col("amount") > 500)
    .otherwise(
        when(col("std_dev") < 0.1, col("amount") > (col("avg_amount") * 2))
        .otherwise(((col("amount") - col("avg_amount")) / col("std_dev")) > 3.0)
    )
)

# 6. WRITE SINK 1: Raw Ingestion
query_all = processed_df.writeStream \
    .format("parquet") \
    .option("path", "hdfs://namenode:9000/data/raw/transactions") \
    .option("checkpointLocation", "hdfs://namenode:9000/checkpoints/all_transactions") \
    .outputMode("append") \
    .start()

# 7. WRITE SINK 2: Fraud Alerts
query_fraud = processed_df.filter(col("is_fraud") == True) \
    .writeStream \
    .format("parquet") \
    .option("path", "hdfs://namenode:9000/data/processed/fraud") \
    .option("checkpointLocation", "hdfs://namenode:9000/checkpoints/fraud_data") \
    .outputMode("append") \
    .start()

print("Streaming System is Live. Writing to HDFS...")
spark.streams.awaitAnyTermination()