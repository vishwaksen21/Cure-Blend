#!/usr/bin/env python3
"""Quick validation test for the diagnosis improvements"""

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer

print("Testing Diagnosis Improvements")
print("=" * 80)

# Load knowledge
knowledge = load_knowledge_base()
print("✓ Knowledge base loaded\n")

# Test cases
tests = [
    ("fever and headache", "Should be low confidence, not Dengue"),
    ("high fever, severe joint pain, eye pain, rash, bleeding gums", "Should be high confidence Dengue"),
]

for symptoms, expected in tests:
    print(f"Test: {symptoms}")
    print(f"Expected: {expected}")
    print("-" * 80)
    
    response = generate_comprehensive_answer(symptoms, knowledge)
    
    disease = response.get('detected_disease', '')
    confidence = response.get('confidence', 0.0)
    ai_insights = response.get('ai_insights', '')
    
    print(f"Detected: {disease}")
    print(f"Confidence: {confidence*100:.1f}%")
    
    # Check for issues
    if "fever and headache" in symptoms.lower():
        if confidence >= 0.40:
            print("❌ FAIL: Confidence too high for generic symptoms")
        elif 'dengue' in disease.lower():
            print("❌ FAIL: Diagnosed as Dengue from generic symptoms")
        else:
            print("✓ PASS: Low confidence, appropriate diagnosis")
    
    elif "severe joint pain" in symptoms.lower():
        if confidence >= 0.40 and 'dengue' in disease.lower():
            print("✓ PASS: High confidence, correct disease")
        else:
            print(f"⚠️  WARNING: Should detect Dengue with high confidence")
    
    # Check AI insights
    if ai_insights:
        has_critical = 'CRITICAL' in ai_insights or 'MEDICATION FOR DENGUE' in ai_insights
        if confidence < 0.40 and has_critical:
            print("❌ FAIL: Disease-specific warnings at low confidence")
        elif confidence >= 0.40 and not has_critical and 'dengue' in disease.lower():
            print("⚠️  Note: High confidence Dengue but no critical warnings")
    
    print()

print("=" * 80)
print("Testing complete!")
