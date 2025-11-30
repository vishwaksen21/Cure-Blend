#!/bin/bash

# Streamlit Web UI - Quick Start Guide

echo "======================================================================"
echo "🌿 CURE-BLEND STREAMLIT WEB UI - LAUNCH SCRIPT"
echo "======================================================================"
echo ""

# Check if streamlit is installed
if ! python -m streamlit --version &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing..."
    pip install streamlit -q
fi

# Kill any existing streamlit processes
echo "🧹 Cleaning up existing processes..."
pkill -f "streamlit run" 2>/dev/null
sleep 2

# Start Streamlit app
echo ""
echo "🚀 Starting Streamlit Web UI..."
echo ""
echo "======================================================================"

cd /workspaces/Cure-Blend
python -m streamlit run streamlit_app.py --server.headless=true --server.port=8501

echo ""
echo "======================================================================"
echo "✅ Streamlit stopped"
echo "======================================================================"
