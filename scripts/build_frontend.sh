#!/bin/bash

# Navigate to the frontend directory
cd ../frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Build the frontend
echo "Building frontend..."
npm run build

# Create the build directory in the backend if it doesn't exist
mkdir -p ../build

# Copy the build files to the backend
echo "Copying build files to backend..."
cp -r build/* ../build/

echo "Frontend build complete and copied to backend."
