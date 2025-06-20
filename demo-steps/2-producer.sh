#!/bin/bash

cd "$(dirname "$0")/.."  # Go to project root

# Run Kafka Producer
echo ""
echo "📤 Starting Kafka Producer..."
pip install -r kafka-producer/requirements.txt
python3 kafka-producer/producer.py

sleep 5

# Verify Kafka Topics
echo ""
echo "📡 Available Kafka Topics:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

echo "  • Streamlit Dashboard → http://localhost:8501"
echo "  • MinIO Console → http://localhost:9001"