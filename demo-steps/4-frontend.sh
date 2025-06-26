#!/bin/bash

echo "🎨 Setting up React Frontend..."
echo ""

# Navigate to react-frontend directory
echo "📁 Navigating to react-frontend directory..."
cd /Users/hazwanadh/Code/Sem4/bigdata/goodreads-book-recommend-bigdata/react-frontend

# Install dependencies
echo "📦 Installing npm dependencies..."
npm install

# Clean and reinstall if needed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo "🧹 Cleaning and reinstalling dependencies..."
    rm -rf node_modules package-lock.json
    npm install
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "� Building frontend to check for errors..."
npm run build

echo ""
echo "�🚀 Starting React Development Server..."
echo "   • Frontend will be available at: http://localhost:3000"
echo "   • Make sure backend is running at: http://localhost:5001"
echo ""
echo "   📱 Available Pages:"
echo "   • Home: Popular books and search"
echo "   • Search: Advanced book search"
echo "   • Popular Books: Trending titles"
echo "   • Recommendations: Get personalized suggestions"
echo "   • Book Details: Full book info with recommendations"
echo ""
echo "   ✨ Features:"
echo "   • Modern responsive UI with Tailwind CSS"
echo "   • Real-time search functionality" 
echo "   • Multiple recommendation algorithms"
echo "   • Interactive book browsing"
echo ""
echo "   • Use Ctrl+C to stop the server"
echo ""

# Start the React development server
npm start
