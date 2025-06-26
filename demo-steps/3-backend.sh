#!/bin/bash

echo "🚀 Starting Backend API Setup..."
echo ""

# Navigate to api-backend directory
echo "📁 Navigating to api-backend directory..."
cd /Users/hazwanadh/Code/Sem4/bigdata/goodreads-book-recommend-bigdata/api-backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "🚀 Starting Flask API Server..."
echo "   • API will be available at: http://localhost:5001"
echo "   • Health check: http://localhost:5001/health"
echo "   • Use Ctrl+C to stop the server"
echo ""

# Start the Flask application
python app.py
