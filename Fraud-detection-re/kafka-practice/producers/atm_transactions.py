from kafka import KafkaProducer
import json
import time
import random

# --- CONFIGURATION FOR THIS SPECIFIC PRODUCER ---
SOURCE_NAME = "ATM"  # Change this to "bank", "mobile", "POS", or "web"
# Center coordinates (e.g., New York City)
BASE_LAT, BASE_LONG = 40.7128, -74.0060 

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# User-specific "Normal" behavior profiles
user_profiles = {
    "user1": {"base_avg": 20, "spread": 5, "city_offset": 0.01},    # Low Spender
    "user2": {"base_avg": 150, "spread": 40, "city_offset": 0.05},  # Med Spender
    "user3": {"base_avg": 800, "spread": 200, "city_offset": 0.1}   # High Spender
}

while True:
    user_id = random.choice(list(user_profiles.keys()))
    profile = user_profiles[user_id]
    
    # 1. GENERATE DYNAMIC AMOUNT
    # Uses a Normal Distribution simulation: base + (random fluctuation)
    amount = round(random.gauss(profile["base_avg"], profile["spread"]), 2)
    amount = max(5, amount) # Ensure no negative transactions
    
    # 2. GENERATE LOCATION (Normal clustering)
    lat = BASE_LAT + random.uniform(-profile["city_offset"], profile["city_offset"])
    lon = BASE_LONG + random.uniform(-profile["city_offset"], profile["city_offset"])

    # 3. INJECT RARE FRAUD (The "Internship" Secret Sauce)
    # 1% chance to create a 5-sigma outlier (Statistical Anomaly)
    is_anomaly = random.random() < 0.01
    if is_anomaly:
        amount = amount * 10  # Sudden spike
        lat += 2.0            # Move location to a different state/region
        print(f"!!! INJECTING ANOMALY for {user_id} !!!")

    event = {
        "user": user_id,
        "amount": amount,
        "source": SOURCE_NAME,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "timestamp": time.time()
    }
    
    producer.send("transactions_partitioned", value=event)
    print(f"[{SOURCE_NAME}] Sent: {event['user']} - ${event['amount']}")
    time.sleep(random.uniform(0.5, 2.0)) # Randomize timing for Poisson logic later