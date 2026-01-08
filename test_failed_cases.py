#!/usr/bin/env python3
"""Test the 3 specific failing cases"""

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer

print("Testing Previously Failed Cases")
print("=" * 80)

knowledge = load_knowledge_base()
print("✓ Knowledge base loaded\n")

# The 3 cases that failed before
test_cases = [
    ("severe headache, joint pain, bleeding gums, fever", "Dengue", 40),
    ("dry cough, loss of taste, loss of smell, fever", "COVID-19", 40),
    ("excessive thirst, frequent urination, fatigue, blurred vision", "Diabetes", 40),
]

passed = 0
failed = 0

for symptoms, expected_disease, min_confidence in test_cases:
    print(f"Test: {symptoms}")
    print(f"Expected: {expected_disease} (confidence >= {min_confidence}%)")
    print("-" * 80)
    
    response = generate_comprehensive_answer(symptoms, knowledge)
    
    disease = response.get('detected_disease', '')
    confidence = response.get('confidence', 0.0) * 100
    
    print(f"Detected: {disease}")
    print(f"Confidence: {confidence:.1f}%")
    
    # Check if correct
    disease_match = expected_disease.lower() in disease.lower()
    confidence_ok = confidence >= min_confidence
    
    if disease_match and confidence_ok:
        print("✅ PASS: Correct disease with adequate confidence")
        passed += 1
    elif disease_match and not confidence_ok:
        print(f"⚠️  PARTIAL: Correct disease but low confidence ({confidence:.1f}%)")
        failed += 1
    else:
        print(f"❌ FAIL: Expected {expected_disease}, got {disease}")
        failed += 1
    
    print()

print("=" * 80)
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("✅ ALL TESTS PASSED!")
else:
    print("⚠️  Some tests still need improvement")
