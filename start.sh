#!/bin/bash
echo "===================================================="
echo "    Starting JalJasoos IoT Platform (Localhost)     "
echo "===================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker is not running or not installed."
  echo "Please start Docker Desktop and try again."
  exit 1
fi

echo "✅ Docker is running. Building and starting containers..."

# Build and start all services in detached mode
docker compose up --build -d

echo "===================================================="
echo "🚀 Services are spinning up!"
echo ""
echo "📍 Cloud API:           http://localhost:8000/docs"
echo "📍 Next.js Dashboard:   http://localhost:3000"
echo "📍 MQTT Broker:         localhost:1883"
echo "📍 Postgres (Cloud):    localhost:5432"
echo "📍 Postgres (Edge):     localhost:5433"
echo ""
echo "To view live logs from the backend and simulator, run:"
echo "  docker compose logs -f api simulator edge-gateway"
echo "===================================================="
