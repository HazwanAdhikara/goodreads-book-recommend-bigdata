#!/bin/bash

echo "🚀 Goodreads Book Recommendation System - Complete Demo"
echo "========================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Demo Overview:${NC}"
echo "1. ✅ Start Backend API (Flask + ML Models)"
echo "2. ✅ Start Frontend (React + TypeScript)"
echo "3. ✅ Test all features"
echo ""

echo -e "${YELLOW}🔧 System Requirements Check:${NC}"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "api-backend" ] || [ ! -d "react-frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo "✅ Project structure verified"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi
echo "✅ Python 3 available"

# Check Node.js
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm is required but not installed${NC}"
    exit 1
fi
echo "✅ Node.js/npm available"

echo ""
echo -e "${BLUE}🎯 Features to Demo:${NC}"
echo "📚 Home Page - Popular books showcase"
echo "🔍 Search - Find books by title, author, or keywords"
echo "📖 Book Details - Full book information with smart covers"
echo "🤖 Recommendations - AI-powered book suggestions"
echo "   • Content-based filtering (LSH)"
echo "   • Collaborative filtering (ALS)"
echo "   • Hybrid approach"
echo "🏆 Popular Books - Trending titles"
echo "💫 Modern UI - Responsive design with Tailwind CSS"
echo ""

echo -e "${YELLOW}🚀 Starting Backend API...${NC}"
echo "Opening backend in new terminal..."

# Start backend in background
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'\"; ./demo-steps/3-backend.sh"'

echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
echo "🔍 Checking backend health..."
BACKEND_HEALTH=$(curl -s http://localhost:5001/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend is running successfully!${NC}"
    echo "Backend response: $BACKEND_HEALTH"
else
    echo -e "${YELLOW}⚠️  Backend might still be starting...${NC}"
    echo "If you see connection errors, wait a bit longer for the backend to fully start."
fi

echo ""
echo -e "${YELLOW}🎨 Starting Frontend...${NC}"
echo "Opening frontend in new terminal..."

# Start frontend in background
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'\"; ./demo-steps/4-frontend.sh"'

echo "⏳ Waiting for frontend to start..."
sleep 8

echo ""
echo -e "${GREEN}🎉 Demo Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📱 Access the Application:${NC}"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5001"
echo ""

echo -e "${BLUE}🧪 Testing Instructions:${NC}"
echo ""
echo "1. 🏠 HOME PAGE (http://localhost:3000)"
echo "   • View popular books with colorful covers"
echo "   • Use the search bar to find books"
echo "   • Click on any book to see details"
echo ""
echo "2. 🔍 SEARCH (http://localhost:3000/search)"
echo "   • Search for books by title, author, or keywords"
echo "   • Try: 'Harry Potter', 'Shakespeare', 'romance'"
echo "   • Click on search results to view details"
echo ""
echo "3. 📖 BOOK DETAILS (Click on any book)"
echo "   • View full book information"
echo "   • See the attractive book cover design"
echo "   • Get AI-powered recommendations"
echo "   • Switch between recommendation methods"
echo ""
echo "4. 🤖 RECOMMENDATIONS (http://localhost:3000/recommendations)"
echo "   • Search for a book you like"
echo "   • Get personalized recommendations"
echo "   • Test different AI algorithms"
echo ""
echo "5. 🏆 POPULAR BOOKS (http://localhost:3000/popular)"
echo "   • Browse trending and highly-rated books"
echo "   • Load more books with pagination"
echo ""

echo -e "${BLUE}🔧 Backend API Endpoints:${NC}"
echo "GET /health - System health check"
echo "GET /books/search?q=<query> - Search books"
echo "GET /books/popular - Get popular books"
echo "GET /books/<id> - Get book details"
echo "GET /books/<id>/recommendations - Get AI recommendations"
echo ""

echo -e "${YELLOW}💡 Troubleshooting:${NC}"
echo "• If you see 'ECONNREFUSED' errors, wait for backend to start"
echo "• If recommendation loading is slow, that's normal (ML processing)"
echo "• Check the terminal windows for detailed logs"
echo "• Use Ctrl+C to stop the servers"
echo ""

echo -e "${GREEN}✨ Performance Improvements Made:${NC}"
echo "🚀 Faster book details loading (separated from recommendations)"
echo "🎨 Beautiful book covers with titles and colors"
echo "⚡ Reduced default recommendation count (6 instead of 12)"
echo "🛡️ Better error handling and graceful degradation"
echo "💫 Improved UI with loading states"
echo ""

echo -e "${BLUE}🎯 Key Features Demonstrated:${NC}"
echo "📊 Big Data Processing: Spark ML for recommendations"
echo "🤖 Machine Learning: LSH + ALS algorithms"
echo "🎨 Modern Frontend: React + TypeScript + Tailwind"
echo "🔄 Real-time API: Flask backend with error handling"
echo "📱 Responsive Design: Works on desktop and mobile"
echo "🎪 Data Visualization: Interactive book browsing"
echo ""

echo -e "${GREEN}🏆 Enjoy exploring your Goodreads Book Recommendation System!${NC}"
echo ""
echo "Opening browser to the application..."
sleep 2
open http://localhost:3000

echo ""
echo -e "${YELLOW}Press any key to continue or Ctrl+C to exit...${NC}"
read -n 1 -s
