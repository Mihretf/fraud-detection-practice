import os
os.environ['HADOOP_USER_NAME'] = 'root'

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("FraudBatchProfiling") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .getOrCreate()

try:
    print("🔄 Updating User Statistical Baselines from HDFS Raw Data...")
    
    # Load all historical transactions from HDFS
    raw_data = spark.read.parquet("hdfs://namenode:9000/data/raw/transactions")
    
    # Calculate means and standard deviations
    user_profiles = raw_data.groupBy("user").agg(
        F.mean("amount").alias("avg_amount"),
        F.stddev("amount").alias("std_dev"),
        F.mean("lat").alias("home_lat"),
        F.mean("lon").alias("home_lon"),
        F.count("amount").alias("transaction_count")
    ).fillna(0) 

    # Save to the 'latest' folder for the Streamer
    user_profiles.write.mode("overwrite").parquet("hdfs://namenode:9000/data/profiles/latest")
    
    print("✅ Profiles updated successfully.")
    user_profiles.show(5)

except Exception as e:
    print(f"❌ Batch Job Failed: {e}")
finally:
    spark.stop()