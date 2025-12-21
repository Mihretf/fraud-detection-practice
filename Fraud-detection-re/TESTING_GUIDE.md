# How to Test the Fraud Detection System

## Quick Start (3 Steps)

### 1. Start Kafka

```bash
cd Fraud-detection-re/kafka-practice
docker-compose up -d
```

Wait 10-15 seconds for Kafka to fully start.

### 2. Start Consumer (Terminal 1)

```bash
cd Fraud-detection-re/kafka-practice
source myenv/bin/activate  # or: . myenv/bin/activate
python consumers/fraud_consumer.py
```

### 3. Start Producers (Terminal 2+)

Open **new terminal windows** for each producer:

**ATM Producer:**
```bash
cd Fraud-detection-re/kafka-practice
source myenv/bin/activate
python producers/atm_transactions.py
```

**Bank Transfer Producer:**
```bash
python producers/bank_transfer.py
```

**Mobile Payments Producer:**
```bash
python producers/mobile_payments.py
```

**POS Terminals Producer:**
```bash
python producers/pos_terminals.py
```

**Web Checkout Producer:**
```bash
python producers/web_checkout.py
```

## What You'll See

**Consumer Output:**
```
Fraud consumer started...
[OK] User=user2 Amount=150 Source=ATM
[FRAUD] User=user1 Amount=750 Source=bank
[OK] User=user3 Amount=200 Source=mobile
```

**Producer Output:**
```
Sent: {'user': 'user1', 'amount': 750, 'source': 'ATM'}
Sent: {'user': 'user2', 'amount': 150, 'source': 'bank'}
```

## Using Spark Streaming (Alternative)

Instead of the Python consumer, you can use Spark:

```bash
cd Fraud-detection-re/spark-streaming-practice/kafka_stream
spark-submit fraud_streaming.py
```

## Stop Everything

- **Producers/Consumers:** Press `Ctrl+C`
- **Kafka:** `docker-compose down` (in kafka-practice folder)

