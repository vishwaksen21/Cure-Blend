#!/usr/bin/env python3
"""
Quick test for pharmaceutical recommendations in terminal
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai_assistant import suggest_drugs_for_disease

print("="*70)
print("🧪 Testing Pharmaceutical Recommendations")
print("="*70)
print()

# Test different conditions
test_conditions = [
    "Tonsillitis",
    "throat pain",
    "Common Cold",
    "fever headache",
    "stomach pain",
    "General Condition"
]

for condition in test_conditions:
    print(f"\n🔍 Testing: {condition}")
    print("-" * 70)
    drugs = suggest_drugs_for_disease(condition, top_n=5)
    
    if drugs:
        print(f"✅ Found {len(drugs)} recommendations:")
        for i, drug in enumerate(drugs, 1):
            print(f"   {i}. {drug['name']} ({drug['type']})")
            print(f"      Purpose: {drug['purpose']}")
    else:
        print(f"❌ No drugs found (THIS IS THE PROBLEM!)")

print("\n" + "="*70)
print("✅ Test Complete!")
print("="*70)
print()
print("If all conditions show drug recommendations, the fix is working!")
print()
