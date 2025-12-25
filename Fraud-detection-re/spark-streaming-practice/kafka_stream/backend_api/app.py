import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
HDFS_BATCH_PATH = "webhdfs://namenode:9870/data/profiles/latest"
HDFS_AUDIT_PATH = "webhdfs://namenode:9870/data/processed/batch_fraud_report"
HDFS_LIVE_MAP_PATH = "webhdfs://namenode:9870/data/processed/fraud"
storage_options = {"user": "root"}

# --- LIVE DATA STORAGE (In-Memory) ---
live_alerts = []
live_stats = {"total_volume": 0, "fraud_count": 0}

# HELPER: Clean data for JSON compliance
def sanitize_df(df):
    # Fills NaNs with 0 and replaces Infinity with 0
    return df.fillna(0).replace([float('inf'), float('-inf')], 0)

# 1. LIVE INGESTION: Receives data from Spark Streamer
@app.post("/api/live-event")
async def receive_live_event(event: dict):
    global live_stats
    live_alerts.insert(0, event) 
    if len(live_alerts) > 15: 
        live_alerts.pop()
    
    live_stats["total_volume"] += event.get("amount", 0)
    live_stats["fraud_count"] += 1
    return {"status": "received"}

# 2. DASHBOARD SUMMARY: Combined stats
@app.get("/api/stats")
async def get_stats():
    return {
        "summary": {
            "total_volume": round(live_stats["total_volume"], 2),
            "fraud_rate": f"{(live_stats['fraud_count'] / 100):.1%}" if live_stats["fraud_count"] > 0 else "0%",
            "fraud_count": live_stats["fraud_count"]
        },
        "recent_fraud": live_alerts
    }

# 3. LIVE MAP DATA: Reads from HDFS streaming output
@app.get("/api/map-data")
async def get_map_data():
    try:
        df = pd.read_parquet(HDFS_LIVE_MAP_PATH, engine='pyarrow', storage_options=storage_options)
        df = sanitize_df(df)
        return {"locations": df.tail(50).to_dict(orient="records")}
    except Exception as e:
        print(f"❌ HDFS Map Error: {e}")
        return {"locations": []}

# 4. USER INTELLIGENCE: Reads the 'Brain' from HDFS
@app.get("/api/batch-report")
async def get_batch_report():
    try:
        df = pd.read_parquet(HDFS_BATCH_PATH, engine='pyarrow', storage_options=storage_options)
        df = sanitize_df(df)
        return {"alerts": df.to_dict(orient="records")}
    except Exception as e:
        print(f"❌ HDFS Profiles Error: {e}")
        return {"alerts": []}

# 5. FRAUD AUDIT: Reads historical flags from HDFS
@app.get("/api/batch-audit")
async def get_batch_audit():
    try:
        df = pd.read_parquet(HDFS_AUDIT_PATH, engine='pyarrow', storage_options=storage_options)
        df = sanitize_df(df)
        fraud_only = df[df['is_fraud'] == True]
        return {"audit": fraud_only.to_dict(orient="records")}
    except Exception as e:
        print(f"❌ HDFS Audit Error: {e}")
        return {"audit": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)