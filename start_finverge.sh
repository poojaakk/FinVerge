#!/bin/bash

echo " Starting FinVerge Procurement Verification System..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo " Error: Please run this script from the FinVerge root directory"
    exit 1
fi

# Start backend server
echo " Starting backend server..."
cd backend

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo " Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start the server in background
echo " Starting FastAPI server on http://localhost:8000..."
python3 run.py &
BACKEND_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo " Backend server is running!"
else
    echo " Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Go back to root directory
cd ..

# Start frontend
echo " Opening web interface..."
if command -v python3 &> /dev/null; then
    echo " Starting frontend server on http://localhost:3000..."
    cd frontend
    python3 -m http.server 3000 &
    FRONTEND_PID=$!
    cd ..
    sleep 2
    
    # Open browser
    if command -v open &> /dev/null; then
        open http://localhost:3000
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    else
        echo " Please open http://localhost:3000 in your browser"
    fi
else
    # Fallback: open HTML file directly
    if command -v open &> /dev/null; then
        open frontend/index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open frontend/index.html
    else
        echo " Please open frontend/index.html in your browser"
    fi
fi

echo ""
echo " FinVerge is now running!"
echo "=================================================="
echo " Backend API: http://localhost:8000"
echo " API Docs: http://localhost:8000/docs"
echo " Frontend: http://localhost:3000 (or frontend/index.html)"
echo ""
echo " To test the system:"
echo "  1. Open the web interface"
echo "  2. Click 'Run Sample Verification'"
echo "  3. Or upload your own PDF documents"
echo ""
echo "⏹️  To stop the servers:"
echo "  Press Ctrl+C or run: pkill -f 'python3 run.py'"
echo ""

# Keep script running
echo " Press Ctrl+C to stop all servers..."
trap "echo ' Stopping servers...'; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for user to stop
wait