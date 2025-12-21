import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LIVE DATA STORAGE (In-Memory) ---
# In a real app, this would be Redis, but a list works for practice!
live_alerts = []
live_stats = {"total_volume": 0, "fraud_count": 0}

HDFS_BATCH_PATH = "webhdfs://localhost:9870/data/reports/daily_velocity_alerts"

# 1. NEW ENDPOINT: This is where your LIVE STREAMING script sends data
@app.post("/api/live-event")
async def receive_live_event(event: dict):
    global live_stats
    # Add to the list of recent fraud
    live_alerts.insert(0, event) 
    if len(live_alerts) > 10: live_alerts.pop() # Keep only latest 10
    
    # Update rolling counters
    live_stats["total_volume"] += event.get("amount", 0)
    live_stats["fraud_count"] += 1
    return {"status": "received"}

# 2. UPDATED STATS: Now it returns the real live data instead of zeros
@app.get("/api/stats")
async def get_stats():
    return {
        "summary": {
            "total_volume": live_stats["total_volume"],
            "fraud_rate": f"{(live_stats['fraud_count'] / 100):.1%}" if live_stats["fraud_count"] > 0 else "0%",
            "fraud_count": live_stats["fraud_count"]
        },
        "recent_fraud": live_alerts
    }

# 3. BATCH REPORT: (Your working HDFS logic)
@app.get("/api/batch-report")
async def get_batch_report():
    try:
        df = pd.read_parquet(
            HDFS_BATCH_PATH, 
            engine='pyarrow', 
            storage_options={"user": "Barney"}
        )
        alerts = df.to_dict(orient="records")
        return {"alerts": alerts}
    except Exception as e:
        print(f"❌ HDFS Connection Error: {e}")
        return {"alerts": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)