# Fraud Detection Kafka Practice

A fraud detection system using Kafka for real-time transaction processing.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ 
- Virtual environment activated (use `myenv` folder)

## Quick Start Guide

### Step 1: Start Kafka Infrastructure

Navigate to the `kafka-practice` directory and start Kafka:

```bash
cd Fraud-detection-re/kafka-practice
docker-compose up -d
```

Wait a few seconds for Kafka to fully start. Verify it's running:

```bash
docker-compose ps
```

### Step 2: Create the Kafka Topic (Optional)

If the topic doesn't exist, Kafka will auto-create it. But you can also create it manually:

```bash
docker exec -it kafka_practice kafka-topics --create \
  --topic transactions_partitioned \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### Step 3: Start the Consumer (in one terminal)

Activate your virtual environment and run the consumer:

```bash
# Windows (Git Bash)
source myenv/bin/activate

# Then run consumer
python consumers/fraud_consumer.py
```

The consumer will listen for transactions and flag any amount > 500 as potential fraud.

### Step 4: Start Producers (in separate terminals)

Open **multiple terminal windows** (one for each producer) and run:

**Terminal 1 - ATM Transactions:**
```bash
source myenv/bin/activate
python producers/atm_transactions.py
```

**Terminal 2 - Bank Transfers:**
```bash
source myenv/bin/activate
python producers/bank_transfer.py
```

**Terminal 3 - Mobile Payments:**
```bash
source myenv/bin/activate
python producers/mobile_payments.py
```

**Terminal 4 - POS Terminals:**
```bash
source myenv/bin/activate
python producers/pos_terminals.py
```

**Terminal 5 - Web Checkout:**
```bash
source myenv/bin/activate
python producers/web_checkout.py
```

### Step 5: Watch the Magic! ✨

You should see:
- Producers sending transaction events every second
- Consumer receiving and analyzing transactions
- `[FRAUD]` messages when amount > 500
- `[OK]` messages for normal transactions

### Alternative: Test with Spark Streaming

Instead of (or in addition to) the Python consumer, you can use Spark Streaming:

```bash
cd ../spark-streaming-practice/kafka_stream
spark-submit fraud_streaming.py
```

## Clean Up

Stop producers and consumer with `Ctrl+C`.

Stop Kafka:
```bash
docker-compose down
```

## Project Structure

```
kafka-practice/
├── producers/          # Transaction producers
│   ├── atm_transactions.py
│   ├── bank_transfer.py
│   ├── mobile_payments.py
│   ├── pos_terminals.py
│   └── web_checkout.py
├── consumers/          # Fraud detection consumer
│   └── fraud_consumer.py
└── docker-compose.yml  # Kafka infrastructure
```

## Troubleshooting

**Kafka connection errors:**
- Make sure Docker containers are running: `docker-compose ps`
- Check if port 9092 is available: `netstat -an | grep 9092`

**Topic not found:**
- Kafka will auto-create topics, but you can manually create them (see Step 2)

**No messages received:**
- Verify all producers are sending to `transactions_partitioned` topic
- Check consumer group ID is correct
- Try resetting offsets: `auto_offset_reset="latest"` or `"earliest"`


