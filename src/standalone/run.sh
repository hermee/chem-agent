#!/bin/bash
# Launch the standalone AI-LNP Agent
# Requires: backend running on :8000
set -e
cd "$(dirname "$0")"
echo "🔨 Building standalone WASM..."
trunk build --release --no-sri
echo "🤖 Starting AI-LNP Agent standalone on http://localhost:8001"
python serve.py
