from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CHANGED: Use webhdfs protocol and port 9870
# Note: 'host.docker.internal' or 'localhost' works here
HDFS_PATH_ALL = "webhdfs://localhost:9870/data/raw/transactions"
HDFS_PATH_FRAUD = "webhdfs://localhost:9870/data/processed/fraud"

def read_hdfs_data(path):
    try:
        # Use storage_options to specify the user (important for permissions)
        # engine='pyarrow' is fine, but it will now use fsspec for the connection
        df = pd.read_parquet(path, engine='pyarrow', storage_options={"user": "root"})
        return df
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return pd.DataFrame()

@app.get("/api/stats")
async def get_stats():
    df_all = read_hdfs_data(HDFS_PATH_ALL)
    df_fraud = read_hdfs_data(HDFS_PATH_FRAUD)
    
    if df_all.empty:
        return {"error": "No data found in HDFS or connection failed"}

    total_transactions = len(df_all)
    fraud_count = len(df_fraud)
    
    return {
        "summary": {
            "total_count": total_transactions,
            "fraud_count": fraud_count,
            "fraud_rate": f"{(fraud_count/total_transactions)*100:.2f}%" if total_transactions > 0 else "0%",
            "total_volume": round(float(df_all['amount'].sum()), 2),
            "fraud_volume": round(float(df_fraud['amount'].sum()), 2) if not df_fraud.empty else 0
        },
        "recent_fraud": df_fraud.tail(10).to_dict(orient="records") if not df_fraud.empty else []
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)