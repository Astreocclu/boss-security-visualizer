#!/bin/bash

# Start the Django backend
echo "Starting Django backend..."
cd ..
python manage.py runserver &
BACKEND_PID=$!

# Start the React frontend
echo "Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!

# Function to handle script termination
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Keep the script running
echo "Development servers are running. Press Ctrl+C to stop."
wait
