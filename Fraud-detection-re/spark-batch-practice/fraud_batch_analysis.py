from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Configuration for stability on a local machine
spark = SparkSession.builder \
    .appName("FraudBatchAnalysis") \
    .master("local[1]") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .getOrCreate()

try:
    print("🚀 Starting Batch Analysis...")
    
    # 1. Read data from HDFS
    # Ensure this path matches where your streaming job is writing
    raw_data = spark.read.parquet("hdfs://localhost:9000/data/raw/transactions")
    
    # 2. Aggregation: Spend per user
    user_history = raw_data.groupBy("user").agg(
        F.sum("amount").alias("total_daily_spend")
    )
    
    # 3. Filter: Users who spent more than $5000 (Velocity Check)
    flagged_users = user_history.filter(F.col("total_daily_spend") > 5000)
    
    # 4. Save the report back to HDFS
    print("💾 Saving Batch Report to HDFS...")
    flagged_users.write.mode("overwrite").parquet("hdfs://localhost:9000/data/reports/daily_velocity_alerts")
    
    print("✅ Batch Report Successfully Created!")
    flagged_users.show() # Display the results in the terminal

except Exception as e:
    print(f"❌ Batch Job Failed: {e}")

finally:
    # Crucial to prevent zombie Java processes
    spark.stop()