#!/bin/bash

echo "🚀 Starting Goodreads Book Recommendation System"
echo "================================================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Run the automation script
echo "🔧 Running automated setup..."
python3 automation.py --action setup

echo ""
echo "🎉 Setup completed! Check the output above for access URLs."
echo ""
echo "📱 Quick Access:"
echo "  • React Frontend:     http://localhost:3000"
echo "  • API Backend:        http://localhost:5000"
echo "  • Streamlit Dashboard: http://localhost:8501"
echo ""
echo "🛑 To stop the system: docker compose down"
