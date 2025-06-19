#!/bin/bash

cd "$(dirname "$0")/.."  # Go to project root

# Run Kafka Producer
echo ""
echo "📤 Starting Kafka Producer..."
python3 kafka-producer/producer.py

sleep 5

# Verify Kafka Topics
echo ""
echo "📡 Available Kafka Topics:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

echo "  • Streamlit Dashboard → http://localhost:8501"
echo "  • Minio Dashboard → http://localhost:9001"