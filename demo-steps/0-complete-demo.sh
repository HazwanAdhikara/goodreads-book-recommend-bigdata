#!/bin/bash

echo "🚀 Goodreads Book Recommendation System - Complete Demo"
echo "======================================================"
echo ""

# Step 1: Start infrastructure
echo "📦 Step 1: Starting Docker infrastructure..."
./demo-steps/1-startdocker.sh

# Wait for services to be fully ready
echo ""
echo "⏳ Waiting for all services to be ready..."
sleep 30

# Check if Kafka is ready
echo "🔍 Checking Kafka readiness..."
until docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 >/dev/null 2>&1; do
    echo "   Waiting for Kafka to be ready..."
    sleep 5
done

echo "✅ Kafka is ready!"

# Step 2: Start producer
echo ""
echo "📤 Step 2: Starting data producer..."
./demo-steps/2-producer.sh &
PRODUCER_PID=$!

# Wait a moment for producer to start
sleep 10

# Give some time for data to be produced
echo ""
echo "⏳ Producing data for 15 seconds..."
sleep 15

# Check if data is in Kafka
echo ""
echo "🔍 Checking Kafka topic data..."
MESSAGE_COUNT=$(docker exec kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic goodreads-books | cut -d: -f3)
echo "📊 Messages in topic: $MESSAGE_COUNT"

if [ "$MESSAGE_COUNT" -gt 0 ]; then
    echo "✅ Data successfully streamed to Kafka!"
else
    echo "⚠️ No data found in Kafka topic"
fi

echo ""
echo "🎉 Demo setup complete!"
echo ""
echo "📱 Access your application:"
echo "  • Streamlit Dashboard → http://localhost:8501"
echo "  • MinIO Console      → http://localhost:9001 (admin: minioadmin/minioadmin)"
echo "  • Spark Master      → http://localhost:8082"
echo "  • Trino UI          → http://localhost:8081"
echo ""
echo "🛑 To stop everything:"
echo "  • Stop producer: kill $PRODUCER_PID"
echo "  • Stop infrastructure: docker compose down"
echo ""

# Keep producer running in background
wait $PRODUCER_PID
