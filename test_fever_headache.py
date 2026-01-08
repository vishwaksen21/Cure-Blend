#!/usr/bin/env python3
"""
Test the improved fever + headache handling
"""

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer

print("=" * 80)
print("TESTING: Fever + Headache Handling")
print("=" * 80)
print()

# Load knowledge base
knowledge = load_knowledge_base()
print("✓ Knowledge base loaded\n")

# Test 1: Generic "fever and headache"
print("TEST 1: Generic symptoms - 'i have fever and headache'")
print("-" * 80)
response = generate_comprehensive_answer("i have fever and headache", knowledge, use_advanced=False)

disease = response.get('detected_disease', '')
confidence = response.get('confidence', 0.0)
confidence_pct = confidence * 100

print(f"  Detected: {disease}")
print(f"  Confidence: {confidence_pct:.1f}%")
print()

# Check if Dengue-specific warnings are present
if 'dengue' in disease.lower():
    print("  ❌ ISSUE: Diagnosed as Dengue with generic symptoms")
else:
    print("  ✓ GOOD: Not diagnosed as Dengue")

if confidence < 0.40:
    print("  ✓ GOOD: Low confidence detected (< 40%)")
else:
    print(f"  ⚠️  WARNING: Confidence is {confidence_pct:.1f}% (should be < 40%)")

print()

# Test 2: Specific dengue symptoms
print("TEST 2: Specific dengue symptoms - 'high fever, severe joint pain, rash, eye pain'")
print("-" * 80)
response2 = generate_comprehensive_answer("high fever, severe joint pain, rash, eye pain", knowledge, use_advanced=False)

disease2 = response2.get('detected_disease', '')
confidence2 = response2.get('confidence', 0.0)
confidence_pct2 = confidence2 * 100

print(f"  Detected: {disease2}")
print(f"  Confidence: {confidence_pct2:.1f}%")
print()

if 'dengue' in disease2.lower() and confidence2 >= 0.40:
    print("  ✓ GOOD: Diagnosed as Dengue with high confidence")
elif 'dengue' in disease2.lower():
    print(f"  ⚠️  WARNING: Dengue detected but confidence low ({confidence_pct2:.1f}%)")
else:
    print("  ❌ ISSUE: Should detect Dengue with these specific symptoms")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
