#!/usr/bin/env python3
"""
Comprehensive test for all major diseases with generic symptoms
Identifies issues similar to the Dengue problem
"""

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer

# Test cases: Generic symptoms that might falsely trigger specific diseases
test_cases = [
    # Generic symptoms
    ("fever", "Should NOT diagnose serious diseases like Dengue/Malaria"),
    ("headache", "Should be generic headache, not serious disease"),
    ("fever and headache", "Should be generic viral infection, not Dengue"),
    ("cough", "Should be common cold/cough, not COVID/TB"),
    ("body ache", "Should be generic pain, not Dengue/Malaria"),
    ("tiredness", "Should be generic fatigue, not serious disease"),
    ("stomach pain", "Should be generic, not specific GI disease"),
    
    # Slightly more specific (but still vague)
    ("high fever", "Could be many things - low confidence expected"),
    ("severe headache", "Could be migraine or tension, not necessarily serious"),
    ("chest pain", "Generic - should warn to seek care but not over-diagnose"),
    ("breathing difficulty", "Generic - should suggest medical evaluation"),
    
    # Disease-specific symptoms (SHOULD diagnose confidently)
    ("high fever, severe joint pain, rash, eye pain, bleeding gums", "Dengue - HIGH confidence"),
    ("intermittent fever, chills, sweating, shivering", "Malaria - HIGH confidence"),
    ("dry cough, loss of taste and smell, fever, fatigue", "COVID-19 - HIGH confidence"),
    ("excessive thirst, frequent urination, fatigue, blurred vision", "Diabetes - HIGH confidence"),
    ("wheezing, shortness of breath, chest tightness", "Asthma - HIGH confidence"),
]

print("=" * 100)
print("COMPREHENSIVE DISEASE DIAGNOSIS TEST")
print("Checking for over-diagnosis from generic symptoms")
print("=" * 100)
print()

# Load knowledge base
knowledge = load_knowledge_base()

issues_found = []
good_cases = []

for i, (symptoms, expected) in enumerate(test_cases, 1):
    print(f"TEST {i}: '{symptoms}'")
    print(f"Expected: {expected}")
    print("-" * 100)
    
    response = generate_comprehensive_answer(symptoms, knowledge, use_advanced=False)
    
    disease = response.get('detected_disease', '')
    confidence = response.get('confidence', 0.0)
    confidence_pct = confidence * 100
    
    print(f"  Detected: {disease}")
    print(f"  Confidence: {confidence_pct:.1f}%")
    
    # Check for potential issues
    disease_lower = disease.lower()
    serious_diseases = ['dengue', 'malaria', 'covid', 'diabetes', 'hypertension', 'asthma', 
                       'typhoid', 'tuberculosis', 'pneumonia', 'meningitis']
    
    is_serious_disease = any(sd in disease_lower for sd in serious_diseases)
    is_generic_symptoms = len(symptoms.split()) <= 3 and 'severe' not in symptoms.lower()
    
    # Issue 1: Serious disease diagnosed with low confidence from generic symptoms
    if is_serious_disease and confidence < 0.40 and is_generic_symptoms:
        issue = f"⚠️  ISSUE: {disease} diagnosed with only {confidence_pct:.1f}% confidence from generic symptoms"
        print(f"  {issue}")
        issues_found.append(f"Test {i}: {issue}")
    
    # Issue 2: High confidence from vague symptoms
    elif confidence >= 0.40 and is_generic_symptoms:
        issue = f"⚠️  ISSUE: High confidence ({confidence_pct:.1f}%) from vague symptoms"
        print(f"  {issue}")
        issues_found.append(f"Test {i}: {issue}")
    
    # Good: Specific symptoms with high confidence
    elif not is_generic_symptoms and confidence >= 0.40:
        print(f"  ✓ GOOD: Specific symptoms + high confidence")
        good_cases.append(f"Test {i}")
    
    # Good: Generic symptoms with low confidence
    elif is_generic_symptoms and confidence < 0.40:
        print(f"  ✓ GOOD: Generic symptoms correctly identified (low confidence)")
        good_cases.append(f"Test {i}")
    
    else:
        print(f"  ℹ️  OK: Reasonable diagnosis")
    
    print()

# Summary
print("=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total tests: {len(test_cases)}")
print(f"Good cases: {len(good_cases)}")
print(f"Issues found: {len(issues_found)}")
print()

if issues_found:
    print("ISSUES DETECTED:")
    for issue in issues_found:
        print(f"  • {issue}")
    print()
    print("❌ FAILED - Issues need to be fixed")
else:
    print("✅ PASSED - All diagnoses appear reasonable")
