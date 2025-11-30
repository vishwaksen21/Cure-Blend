#!/bin/bash

# Quick Start Script for Streamlit Web UI
# Run this to launch the Cure-Blend web application

echo "========================================"
echo "🚀 Starting Cure-Blend Web Application"
echo "========================================"
echo ""

# Kill any existing process on port 8502
lsof -ti:8502 | xargs kill -9 2>/dev/null

# Start Streamlit
echo "📦 Loading application..."
python -m streamlit run streamlit_app.py \
    --server.port 8502 \
    --server.address 0.0.0.0 \
    --server.headless true

# Note: The server will start and show the URL
# In GitHub Codespaces, VS Code will show a popup to open the port
