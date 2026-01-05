#!/bin/bash
# Quick deployment script for Cure-Blend

echo "========================================="
echo "🚀 Cure-Blend Deployment Helper"
echo "========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Production ready Cure-Blend"
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Check git remote
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  No remote repository configured"
    echo "Please run:"
    echo "  git remote add origin https://github.com/vishwaksen21/Cure-Blend.git"
    echo "  git push -u origin main"
else
    echo "✅ Git remote configured"
fi

echo ""
echo "========================================="
echo "📋 Deployment Options:"
echo "========================================="
echo ""
echo "1️⃣  Streamlit Cloud (RECOMMENDED - FREE)"
echo "   → Go to: https://share.streamlit.io/"
echo "   → Click 'New app'"
echo "   → Select your GitHub repo"
echo "   → Deploy!"
echo ""
echo "2️⃣  Docker (Local/Cloud)"
echo "   → docker build -t cure-blend ."
echo "   → docker run -p 8501:8501 cure-blend"
echo ""
echo "3️⃣  Docker Compose"
echo "   → docker-compose up -d"
echo ""
echo "4️⃣  Heroku"
echo "   → heroku create cure-blend-app"
echo "   → git push heroku main"
echo ""
echo "========================================="
echo "📊 Current Status:"
echo "========================================="
echo ""

# Check if app is running
if pgrep -f "streamlit" > /dev/null; then
    echo "✅ Streamlit app is running locally"
    echo "   URL: http://localhost:8501"
else
    echo "⚠️  Streamlit app is not running"
    echo "   Run: streamlit run streamlit_app.py"
fi

echo ""

# Check data files
if [ -d "data" ]; then
    echo "✅ Data directory exists"
    DATA_SIZE=$(du -sh data/ | cut -f1)
    echo "   Size: $DATA_SIZE"
else
    echo "⚠️  Data directory not found"
fi

echo ""

# Check requirements
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists"
    REQ_COUNT=$(wc -l < requirements.txt)
    echo "   Dependencies: $REQ_COUNT"
else
    echo "⚠️  requirements.txt not found"
fi

echo ""

# Check deployment files
echo "📦 Deployment files:"
[ -f "Dockerfile" ] && echo "   ✅ Dockerfile" || echo "   ❌ Dockerfile"
[ -f "docker-compose.yml" ] && echo "   ✅ docker-compose.yml" || echo "   ❌ docker-compose.yml"
[ -f "Procfile" ] && echo "   ✅ Procfile (Heroku)" || echo "   ❌ Procfile"
[ -f "runtime.txt" ] && echo "   ✅ runtime.txt" || echo "   ❌ runtime.txt"
[ -f ".streamlit/config.toml" ] && echo "   ✅ .streamlit/config.toml" || echo "   ❌ .streamlit/config.toml"

echo ""
echo "========================================="
echo "🎯 Next Steps:"
echo "========================================="
echo ""
echo "For Streamlit Cloud (Easiest):"
echo "  1. Push to GitHub (if not already done)"
echo "  2. Visit https://share.streamlit.io/"
echo "  3. Connect GitHub and select this repo"
echo "  4. Click Deploy"
echo ""
echo "For Docker:"
echo "  docker build -t cure-blend ."
echo "  docker run -p 8501:8501 cure-blend"
echo ""
echo "For full guide, see: DEPLOYMENT_GUIDE.md"
echo ""
echo "========================================="
echo "✅ Ready to deploy!"
echo "========================================="
