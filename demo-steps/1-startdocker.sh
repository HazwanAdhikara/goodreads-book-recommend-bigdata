#!/bin/bash

cd "$(dirname "$0")/.."  # Go to project root

echo ""
echo "🚀 Starting Goodreads Book Recommendation System"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

# Run Docker Compose
echo "🔧 Launching containers using Docker Compose..."
docker compose up --build -d

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# List running containers
echo ""
echo "📦 Currently running containers:"
docker compose ps

echo "🛑 To stop the system: run → docker compose down"

