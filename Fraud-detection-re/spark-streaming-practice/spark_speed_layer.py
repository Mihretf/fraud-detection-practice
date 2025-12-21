from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import requests

# 1. Setup Spark with Kafka Connector
spark = SparkSession.builder \
    .appName("FraudSpeedLayer") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .getOrCreate()

schema = StructType([
    StructField("user", StringType(), True),
    StructField("amount", IntegerType(), True),
    StructField("source", StringType(), True)
])

# 2. Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transactions_partitioned") \
    .load()

# 3. Parse JSON
clean_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 4. Function to send data to FastAPI
def send_to_fastapi(batch_df, batch_id):
    # Convert batch to list of dicts
    rows = batch_df.collect()
    for row in rows:
        payload = {"user": row.user, "amount": row.amount, "type": "FRAUD_ALERT"}
        try:
            requests.post("http://localhost:8000/api/live-event", json=payload)
        except Exception as e:
            print(f"Error connecting to API: {e}")

# 5. Start the Stream
query = clean_df.writeStream \
    .foreachBatch(send_to_fastapi) \
    .start()

print("🚀 Speed Layer is bridging Kafka to Dashboard...")
query.awaitTermination()