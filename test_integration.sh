#!/bin/bash

# Quick Test: Verify Advanced Features Integration in main.py
# This simulates manual interactive testing

echo "=================================="
echo "Testing Advanced Features in main.py"
echo "=================================="
echo ""
echo "This will test with pregnant patient having UTI symptoms"
echo "Expected output:"
echo "  ✅ Basic herbal + pharma recommendations"
echo "  ✅ Multi-disease analysis (UTI primary)"
echo "  ✅ Severity assessment (Mild)"
echo "  ✅ Personalized warnings (9 contraindicated drugs)"
echo ""
echo "Press Ctrl+C to stop, or wait for automatic input..."
echo ""
sleep 2

# Run main.py with simulated input
# Note: Use echo with actual newlines, not escape sequences
(
  echo "y"  # Use advanced features
  echo "y"  # Create patient profile
  echo "28"  # Age
  echo "female"  # Gender
  echo "y"  # Pregnant
  echo "n"  # Not breastfeeding
  echo "n"  # No diabetes
  echo "n"  # No hypertension
  echo "n"  # No kidney disease
  echo "frequent urination burning sensation lower abdominal discomfort"  # Symptoms
  sleep 2
  echo "n"  # Don't show JSON
  echo "quit"  # Exit
) | python /workspaces/Cure-Blend/main.py

echo ""
echo "=================================="
echo "Test Complete"
echo "=================================="
echo ""
echo "✅ If you saw 'ADVANCED ANALYSIS' section with:"
echo "   • Multi-disease analysis"
echo "   • Severity assessment"
echo "   • Personalized recommendations"
echo "   Then integration is SUCCESSFUL!"
echo ""
echo "❌ If you only saw basic recommendations without"
echo "   'ADVANCED ANALYSIS' header, check:"
echo "   • sys.stdin.isatty() may return False in pipe mode"
echo "   • Need to run python main.py manually in terminal"
