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
    
    # 1. Load all historical transactions from HDFS 
    # Using /*.parquet to avoid metadata/checkpoint conflicts
    raw_data = spark.read.parquet("hdfs://namenode:9000/data/raw/transactions/*.parquet")
    
    # 2. Calculate means and standard deviations (The Baselines)
    user_profiles = raw_data.groupBy("user").agg(
        F.mean("amount").alias("avg_amount"),
        F.stddev("amount").alias("std_dev"),
        F.mean("lat").alias("home_lat"),
        F.mean("lon").alias("home_lon"),
        F.count("amount").alias("transaction_count")
    ).fillna(0) 

    # Save to the 'latest' folder for the Streamer to use as a lookup
    user_profiles.write.mode("overwrite").parquet("hdfs://namenode:9000/data/profiles/latest")
    print("✅ Reference profiles saved for Streaming layer.")

    # --- STEP 3: BATCH FLAGGING (Historical Audit) ---
    # We alias raw_data as 'raw' and user_profiles as 'prof' to prevent ambiguity
    batch_audit = raw_data.alias("raw").join(
        user_profiles.alias("prof"), 
        on="user", 
        how="inner"
    ).withColumn("is_fraud", 
        (F.col("raw.amount") > (F.col("prof.avg_amount") + 3 * F.col("prof.std_dev")))
    )

    # Filter for only the suspicious ones and select columns from the 'raw' side
    # to avoid saving duplicate baseline columns in the report
    fraudulent_audit = batch_audit.filter(F.col("is_fraud") == True).select("raw.*", "is_fraud")

    # Save the Batch Fraud Report to HDFS
    fraudulent_audit.write.mode("overwrite").parquet("hdfs://namenode:9000/data/processed/batch_fraud_report")

    print("✅ Batch Fraud Audit Complete. Results saved to HDFS.")
    print("✅ Profiles updated successfully.")
    
    # Show results in terminal for verification
    user_profiles.show(5)

except Exception as e:
    print(f"❌ Batch Job Failed: {e}")
finally:
    spark.stop()