#!/bin/bash
echo "===================================================="
echo "    Starting JalJasoos NATIVELY (100% Docker-Free)  "
echo "===================================================="

# 1. Install Python dependencies
echo "🐍 Verifying Python dependencies..."
pip install -q -e packages/mqtt-contracts
pip install -q -e apps/api
pip install -q -e apps/edge-gateway
pip install -q -e apps/simulator

# 2. Start Backend Services (using SQLite and Public MQTT for Mac fallback)
echo "🚀 Starting Cloud API (Port 8000)..."
export DATABASE_URL="sqlite:///./jaljasoos_cloud.db"
(cd apps/api && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > api.log 2>&1) &
API_PID=$!

echo "🚀 Starting Edge Gateway (Port 8080)..."
export EDGE_DATABASE_URL="sqlite:///./jaljasoos_edge.db"
export MQTT_BROKER_HOST="broker.hivemq.com"
export CLOUD_API_URL="http://127.0.0.1:8000"
export CLOUD_WS_URL="ws://127.0.0.1:8000"
(cd apps/edge-gateway && python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 > edge.log 2>&1) &
EDGE_PID=$!

echo "🚀 Starting Physics Simulator..."
export MQTT_BROKER_HOST="broker.hivemq.com"
export SIM_SOCIETY_ID=society01
export SIM_BUILDING_ID=buildingA
export SIM_SCENARIO=normal
(cd apps/simulator && python -m simulator.main > sim.log 2>&1) &
SIM_PID=$!

echo "===================================================="
echo "✅ All Native Services Running (No Docker Used!)"
echo "✅ Using local SQLite and public HiveMQ broker."
echo "===================================================="
echo ""
echo "To start the frontend Dashboard, please open ONE MORE new terminal and run:"
echo "  cd /Users/harshshinde/Downloads/SIH-2026/apps/web"
echo "  npm install"
echo "  npm run dev"
echo ""

# Trap Ctrl+C to kill the background python processes
trap "echo 'Shutting down natively...'; kill $API_PID $EDGE_PID $SIM_PID; docker compose stop; exit" INT
wait
