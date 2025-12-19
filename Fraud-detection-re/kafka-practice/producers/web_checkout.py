from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

users = ["user1", "user2", "user3"]

while True:
    event = {
        "user": random.choice(users),
        "amount": random.randint(10, 1000),
        "source": "web"
    }
    producer.send("transactions_partitioned", value=event)
    print(f"Sent: {event}")
    time.sleep(1)
