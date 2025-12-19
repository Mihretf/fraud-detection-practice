from kafka import KafkaConsumer
import json

TOPIC_NAME = "transactions"
BOOTSTRAP_SERVERS = "localhost:9092"

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="fraud-detector-v2",
    enable_auto_commit=True
)

print("Fraud consumer started...")

for message in consumer:
    try:
        event = message.value
        user = event.get("user")
        amount = event.get("amount")
        source = event.get("source")

        if amount is not None and amount > 500:
            print(f"[FRAUD] User={user} Amount={amount} Source={source}")
        else:
            print(f"[OK] User={user} Amount={amount} Source={source}")

    except Exception as e:
        print(f"[SKIPPED] Invalid message: {message.value}")
