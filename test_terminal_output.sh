#!/bin/bash
# Test the terminal recommendations output

echo "======================================================================"
echo "🧪 Testing Cure-Blend Terminal Recommendations"
echo "======================================================================"
echo ""

cd "$(dirname "$0")"

echo "1️⃣  Running recommendation test..."
echo ""
python3 test_recommendations.py
echo ""

echo "======================================================================"
echo "2️⃣  Now testing main.py with sample input..."
echo "======================================================================"
echo ""

# Test main.py with piped input
echo "fever headache body ache fatigue" | python3 main.py

echo ""
echo "======================================================================"
echo "✅ Test Complete!"
echo "======================================================================"
echo ""
echo "If you see herbal and pharma recommendations above, it's working!"
echo "If not, there may be data file issues."
echo ""
echo "To run interactively:"
echo "  python3 main.py"
echo ""
