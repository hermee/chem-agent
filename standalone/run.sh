#!/bin/bash
# Launch the standalone AI-LNP Agent
# Requires: backend running on :8000
set -e
cd "$(dirname "$0")"
echo "🤖 Starting AI-LNP Agent standalone on http://localhost:4300"
../.venv/bin/python serve.py
