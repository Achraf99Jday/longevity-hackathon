#!/bin/bash
# Quick start script for local testing

echo "🚀 Starting Longevity R&D Map Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -c "from longevity_map.database.session import init_db; init_db()"

# Start API server in background
echo "🌐 Starting API server on http://localhost:8000..."
python scripts/run_api.py &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start web server
echo "📱 Starting web interface on http://localhost:3000..."
cd public
python -m http.server 3000 &
WEB_PID=$!

echo ""
echo "✅ Platform is running!"
echo "   API: http://localhost:8000"
echo "   Web: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $API_PID $WEB_PID; exit" INT
wait


