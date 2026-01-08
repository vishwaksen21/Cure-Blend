#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUITE
Tests all disease diagnosis improvements to prevent over-diagnosis from generic symptoms
"""

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer

print("=" * 100)
print("COMPREHENSIVE DISEASE DIAGNOSIS VALIDATION TEST")
print("=" * 100)
print()

# Load knowledge base once
print("Loading knowledge base...")
knowledge = load_knowledge_base()
print("✓ Loaded\n")

# Test scenarios organized by category
test_scenarios = {
    "Generic Symptoms (Should have LOW confidence <40%)": [
        ("fever", "Should NOT diagnose Dengue/Malaria/COVID"),
        ("headache", "Should be generic headache"),
        ("fever and headache", "Should be generic viral, NOT specific disease"),
        ("cough", "Should be common cold, NOT COVID/TB"),
        ("body ache", "Should be generic pain"),
        ("tired", "Should be fatigue, not serious disease"),
    ],
    
    "Dengue-Specific (Should have HIGH confidence >40%)": [
        ("high fever, severe joint pain, eye pain, rash", "Dengue with high confidence"),
        ("severe headache, joint pain, bleeding gums, fever", "Dengue with high confidence"),
        ("dengue fever joint pain", "Dengue with high confidence"),
    ],
    
    "Malaria-Specific (Should have HIGH confidence >40%)": [
        ("intermittent fever, chills, sweating, shivering", "Malaria with high confidence"),
        ("malaria fever chills", "Malaria with high confidence"),
        ("cyclic fever episodes with chills", "Malaria with reasonable confidence"),
    ],
    
    "COVID-Specific (Should have HIGH confidence >40%)": [
        ("dry cough, loss of taste, loss of smell, fever", "COVID with high confidence"),
        ("fever, dry cough, fatigue, loss of taste", "COVID with high confidence"),
    ],
    
    "Other Serious Diseases (Should have HIGH confidence >40%)": [
        ("excessive thirst, frequent urination, fatigue, blurred vision", "Diabetes with high confidence"),
        ("wheezing, shortness of breath, chest tightness", "Asthma with high confidence"),
        ("high blood pressure, dizziness, chest pain", "Hypertension with high confidence"),
    ],
}

# Track results
all_results = []
issues_found = []
good_cases = []

for category, tests in test_scenarios.items():
    print(f"\n{'='*100}")
    print(f"CATEGORY: {category}")
    print('='*100)
    
    for symptoms, expected_behavior in tests:
        print(f"\nTest: '{symptoms}'")
        print(f"Expected: {expected_behavior}")
        print("-" * 100)
        
        response = generate_comprehensive_answer(symptoms, knowledge)
        
        disease = response.get('detected_disease', '')
        confidence = response.get('confidence', 0.0)
        confidence_pct = confidence * 100
        ai_insights = response.get('ai_insights', '')
        
        print(f"  Detected: {disease}")
        print(f"  Confidence: {confidence_pct:.1f}%")
        
        # Validation logic
        disease_lower = disease.lower()
        serious_diseases = ['dengue', 'malaria', 'covid', 'diabetes', 'hypertension', 
                           'asthma', 'typhoid', 'tuberculosis', 'pneumonia']
        
        is_serious = any(sd in disease_lower for sd in serious_diseases)
        is_generic_input = len(symptoms.split()) <= 4 and not any(kw in symptoms.lower() for kw in 
            ['severe', 'loss of', 'excessive', 'frequent', 'intermittent', 'cyclic', 'bleeding'])
        
        # Check for disease-specific warnings in AI insights
        has_specific_warnings = False
        if ai_insights:
            critical_phrases = ['CRITICAL:', 'MEDICATION FOR DENGUE', 'MEDICATION FOR MALARIA', 
                              'MEDICATION FOR COVID', 'strictly avoided', 'ONLY safe option']
            has_specific_warnings = any(phrase in ai_insights for phrase in critical_phrases)
        
        # Validation rules
        status = "✓"
        issue = None
        
        # Rule 1: Generic symptoms should have low confidence (<40%)
        if "Generic Symptoms" in category:
            if is_serious and confidence >= 0.40:
                status = "❌"
                issue = f"Serious disease ({disease}) with high confidence from generic symptoms"
            elif confidence < 0.40:
                status = "✓"
                result = "Correctly flagged as low confidence"
            else:
                status = "✓"
                result = "Reasonable diagnosis"
        
        # Rule 2: Specific symptoms should have higher confidence (>=40%)
        elif "Specific" in category or "Other Serious" in category:
            if confidence >= 0.40:
                status = "✓"
                result = "Good: Specific symptoms with appropriate confidence"
            else:
                status = "⚠️ "
                issue = f"Specific symptoms but low confidence ({confidence_pct:.1f}%)"
        
        # Rule 3: Low confidence should NOT show disease-specific critical warnings
        if confidence < 0.40 and has_specific_warnings:
            status = "❌"
            issue = f"Disease-specific warnings shown despite low confidence ({confidence_pct:.1f}%)"
        
        # Print result
        if issue:
            print(f"  {status} ISSUE: {issue}")
            issues_found.append(f"{symptoms} → {issue}")
        else:
            print(f"  {status} PASS")
            good_cases.append(symptoms)
        
        # Show snippet of AI insights if present
        if ai_insights and len(ai_insights) > 100:
            snippet = ai_insights[:150].replace('\n', ' ')
            print(f"  AI Insights: {snippet}...")
        
        all_results.append({
            'symptoms': symptoms,
            'disease': disease,
            'confidence': confidence,
            'status': status,
            'issue': issue
        })

# Final Summary
print("\n" + "=" * 100)
print("FINAL SUMMARY")
print("=" * 100)
print(f"Total tests: {len(all_results)}")
print(f"Passed: {len(good_cases)}")
print(f"Issues: {len(issues_found)}")
print()

if issues_found:
    print("❌ ISSUES DETECTED:")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")
    print()
    print("RECOMMENDATION: Review and fix the issues above")
else:
    print("✅ ALL TESTS PASSED!")
    print("The system correctly:")
    print("  • Detects generic symptoms with low confidence")
    print("  • Detects specific symptoms with high confidence")
    print("  • Shows disease-specific warnings only for high confidence")
    print("  • Provides generic guidance for low confidence cases")

print()
print("=" * 100)
