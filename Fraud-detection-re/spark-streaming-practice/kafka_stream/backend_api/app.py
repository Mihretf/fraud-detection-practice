import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Enable CORS so your React Frontend (usually port 3000/5173) can talk to this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LIVE DATA STORAGE (In-Memory) ---
live_alerts = []
live_stats = {"total_volume": 0, "fraud_count": 0}

# Update this path to your new profiles location
HDFS_BATCH_PATH = "webhdfs://namenode:9870/data/profiles/latest"
storage_options = {"user": "root"}

# 1. LIVE INGESTION: Receives data from Spark Streamer
@app.post("/api/live-event")
async def receive_live_event(event: dict):
    global live_stats
    # We keep the latest 15 alerts to ensure the dashboard looks full
    live_alerts.insert(0, event) 
    if len(live_alerts) > 15: 
        live_alerts.pop()
    
    live_stats["total_volume"] += event.get("amount", 0)
    live_stats["fraud_count"] += 1
    return {"status": "received"}

# 2. DASHBOARD SUMMARY: Combined stats for the top cards
@app.get("/api/stats")
async def get_stats():
    # Adding a simulated fraud rate based on count
    return {
        "summary": {
            "total_volume": round(live_stats["total_volume"], 2),
            "fraud_rate": f"{(live_stats['fraud_count'] / 100):.1%}" if live_stats["fraud_count"] > 0 else "0%",
            "fraud_count": live_stats["fraud_count"]
        },
        "recent_fraud": live_alerts
    }

# 3. STATISTICAL PROFILES: Reads the 'Brain' from HDFS
@app.get("/api/batch-report")
async def get_batch_report():
    try:
        # SACRED LOGIC: Keeping your Barney user and pyarrow engine
        df = pd.read_parquet(
            HDFS_BATCH_PATH, 
            engine='pyarrow', 
            storage_options=storage_options
        )
        
        # We convert the dataframe to a list of dicts. 
        # This now includes avg_amount, std_dev, and transaction_count
        profiles = df.to_dict(orient="records")
        return {"alerts": profiles}
        
    except Exception as e:
        # We print the error for debugging but return empty list so UI doesn't crash
        print(f"❌ HDFS Connection Error: {e}")
        return {"alerts": []}

if __name__ == "__main__":
    # Standard Uvicorn startup
    uvicorn.run(app, host="0.0.0.0", port=8000)