#!/bin/bash
# Run the Reactome LNP Agent
# Backend: FastAPI on :8000
# Frontend: Angular on :4200

set -e
cd "$(dirname "$0")"

unset CUDA_VISIBLE_DEVICES

echo "🧬 Starting Reactome LNP Agent..."
echo ""

# Start backend
echo "Starting backend (FastAPI + LangGraph)..."
.venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID → http://localhost:8000/docs"

# Start frontend
echo "Starting frontend (Angular)..."
cd src/frontend/reactome-ui
ng serve --port 4200 --open &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID → http://localhost:4200"

cd ../../..

echo ""
echo "✅ Both servers running. Press Ctrl+C to stop."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
