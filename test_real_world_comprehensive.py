#!/usr/bin/env python3
"""
COMPREHENSIVE REAL-WORLD TEST SUITE
Tests complex inputs, edge cases, and ambiguous scenarios
"""

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer
import json

print("=" * 100)
print("COMPREHENSIVE REAL-WORLD DIAGNOSIS TEST")
print("Testing complex inputs, edge cases, and ambiguous scenarios")
print("=" * 100)
print()

# Load knowledge base
knowledge = load_knowledge_base()
print("✓ Knowledge base loaded\n")

# Comprehensive test scenarios
test_categories = {
    "1. COMPLEX MULTI-SYMPTOM INPUTS": [
        ("I've been having high fever for 3 days, severe body aches, joint pain especially in knees, headache behind my eyes, and noticed small red spots on my skin", 
         "Dengue", 50, "Complex dengue presentation"),
        
        ("My symptoms started 5 days ago with dry cough, then lost my sense of smell completely, can't taste anything, feeling very tired, mild fever comes and goes",
         "COVID-19", 50, "Complex COVID presentation"),
        
        ("For the past 2 weeks I'm constantly thirsty, drinking lots of water but still thirsty, going to bathroom every hour especially at night, vision is blurry, feeling weak and tired",
         "Diabetes", 50, "Classic diabetes triad with additional symptoms"),
        
        ("I get sudden episodes of fever that come and go every 2-3 days, chills so bad I'm shivering, then I start sweating heavily, headache and body pain",
         "Malaria", 40, "Cyclic fever pattern"),
    ],
    
    "2. AMBIGUOUS / OVERLAPPING SYMPTOMS": [
        ("fever, cough, body ache, fatigue",
         None, 40, "Could be flu, COVID, or other viral - should NOT be highly confident"),
        
        ("chest pain, shortness of breath, dizziness",
         None, 40, "Could be cardiac, anxiety, or respiratory - should warn to seek care"),
        
        ("stomach pain, nausea, loss of appetite",
         None, 40, "Generic GI symptoms - low confidence expected"),
        
        ("headache, dizziness, fatigue",
         None, 40, "Very generic - should be low confidence"),
    ],
    
    "3. EDGE CASES - SINGLE DISTINCTIVE SYMPTOM": [
        ("I can't smell anything at all",
         "COVID-19", 40, "Anosmia is highly specific for COVID"),
        
        ("bleeding from my gums",
         None, 40, "Single bleeding symptom without fever - should be cautious"),
        
        ("intermittent fever that comes every other day",
         "Malaria", 30, "Cyclic fever pattern suggests malaria"),
    ],
    
    "4. NATURAL LANGUAGE / CONVERSATIONAL": [
        ("not feeling well for a few days, kind of tired and weak",
         None, 30, "Very vague - should be very low confidence"),
        
        ("I think I might have dengue because I have fever and my joints hurt a lot and I saw some bleeding",
         "Dengue", 60, "User mentions dengue + multiple symptoms"),
        
        ("Doctor said to monitor my blood sugar because I'm peeing a lot and always thirsty",
         "Diabetes", 50, "Context clues about diabetes"),
        
        ("My asthma is acting up, wheezing and can't breathe properly",
         "Asthma", 50, "User self-identifies condition"),
    ],
    
    "5. DISEASE CONFUSION SCENARIOS": [
        ("high fever, vomiting, diarrhea, abdominal pain, weakness",
         "Typhoid", 30, "Could be typhoid, gastroenteritis, or food poisoning"),
        
        ("fever, cough, difficulty breathing, chest pain",
         None, 40, "Could be pneumonia, COVID, or other respiratory - multiple possibilities"),
        
        ("joint pain, muscle pain, fatigue, no fever",
         None, 35, "Could be arthritis, fibromyalgia, or other - low specificity"),
    ],
    
    "6. SEVERITY VARIATIONS": [
        ("mild headache",
         "Headache", 25, "Mild symptom - low confidence"),
        
        ("severe crushing chest pain, sweating, left arm pain",
         None, 50, "Emergency symptoms - should flag for immediate care"),
        
        ("extremely high fever 104F, severe joint pain, bleeding from nose and gums",
         "Dengue", 70, "Severe dengue presentation"),
    ],
    
    "7. CHRONIC VS ACUTE": [
        ("I've had high blood pressure for years, now getting headaches and dizziness",
         "Hypertension", 50, "Chronic condition with symptoms"),
        
        ("sudden onset of severe headache, worst headache of my life",
         None, 40, "Emergency headache - should recommend immediate care"),
        
        ("pain when urinating for 2 days, lower back pain, cloudy urine",
         "UTI", 50, "Acute UTI presentation"),
    ],
    
    "8. PEDIATRIC / AGE-SPECIFIC": [
        ("my child has fever, rash, runny nose, cough",
         None, 35, "Could be measles, viral infection, or other - multiple possibilities"),
        
        ("baby is crying a lot, pulling at ear, fever",
         None, 40, "Suggests ear infection but not in our disease list"),
    ],
    
    "9. NEGATION / ABSENT SYMPTOMS": [
        ("fever but no cough, no cold symptoms",
         None, 25, "Negative symptoms - limits differential"),
        
        ("high fever without any rash or bleeding",
         None, 30, "Excludes dengue hemorrhagic features"),
    ],
    
    "10. UNCOMMON PRESENTATIONS": [
        ("I feel feverish but thermometer shows normal temperature, body aches, can't taste food properly",
         "COVID-19", 35, "Subjective fever with anosmia"),
        
        ("no fever but severe joint pain in multiple joints, rash on arms and legs",
         None, 30, "Atypical presentation - no fever complicates diagnosis"),
        
        ("I had dengue 2 months ago, now again having fever and body pain",
         "Dengue", 40, "Recurrent dengue - relevant history"),
    ],
}

# Track results
total_tests = 0
passed = 0
warnings = 0
failed = 0
results_log = []

for category, tests in test_categories.items():
    print(f"\n{'='*100}")
    print(f"{category}")
    print('='*100)
    
    for symptoms, expected_disease, confidence_threshold, description in tests:
        total_tests += 1
        print(f"\n{total_tests}. {description}")
        print(f"   Input: '{symptoms}'")
        print(f"   Expected: {expected_disease or 'Low confidence / Generic'} (conf >= {confidence_threshold}%)")
        print("-" * 100)
        
        try:
            response = generate_comprehensive_answer(symptoms, knowledge)
            
            disease = response.get('detected_disease', '')
            confidence = response.get('confidence', 0.0)
            confidence_pct = confidence * 100
            ai_insights = response.get('ai_insights', '')
            
            print(f"   Detected: {disease}")
            print(f"   Confidence: {confidence_pct:.1f}%")
            
            # Validation logic
            status = "✓"
            issue = None
            
            if expected_disease:
                # Expected specific disease
                disease_match = expected_disease.lower() in disease.lower()
                confidence_ok = confidence_pct >= confidence_threshold
                
                if disease_match and confidence_ok:
                    status = "✓"
                    result = "PASS"
                    passed += 1
                elif disease_match and not confidence_ok:
                    status = "⚠️"
                    issue = f"Correct disease but confidence too low ({confidence_pct:.1f}% < {confidence_threshold}%)"
                    result = "WARNING"
                    warnings += 1
                else:
                    status = "❌"
                    issue = f"Wrong disease: expected {expected_disease}, got {disease}"
                    result = "FAIL"
                    failed += 1
            else:
                # Expected low confidence / generic
                if confidence_pct < confidence_threshold:
                    status = "✓"
                    result = "PASS"
                    passed += 1
                else:
                    status = "⚠️"
                    issue = f"Confidence too high for ambiguous symptoms ({confidence_pct:.1f}%)"
                    result = "WARNING"
                    warnings += 1
            
            # Check for inappropriate warnings at low confidence
            if confidence_pct < 40:
                critical_warnings = ['CRITICAL:', 'MEDICATION FOR DENGUE', 'MEDICATION FOR MALARIA', 
                                   'MEDICATION FOR COVID', 'strictly avoided', 'ONLY safe option']
                has_critical = any(phrase in (ai_insights or '') for phrase in critical_warnings)
                
                if has_critical:
                    status = "❌"
                    issue = (issue or "") + " | Disease-specific warnings at low confidence"
                    result = "FAIL"
                    if result != "FAIL":
                        failed += 1
            
            print(f"   {status} {result}", end="")
            if issue:
                print(f": {issue}")
            else:
                print()
            
            # Log result
            results_log.append({
                'test_num': total_tests,
                'description': description,
                'symptoms': symptoms,
                'detected': disease,
                'confidence': confidence_pct,
                'expected': expected_disease,
                'status': result,
                'issue': issue
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
            results_log.append({
                'test_num': total_tests,
                'description': description,
                'symptoms': symptoms,
                'error': str(e),
                'status': 'ERROR'
            })

# Final Summary
print("\n" + "=" * 100)
print("FINAL SUMMARY")
print("=" * 100)
print(f"Total tests: {total_tests}")
print(f"✓ Passed: {passed}")
print(f"⚠️  Warnings: {warnings}")
print(f"❌ Failed: {failed}")
print()

pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
print(f"Pass rate: {pass_rate:.1f}%")

if failed > 0:
    print(f"\n❌ {failed} CRITICAL FAILURES")
    print("Failed tests:")
    for r in results_log:
        if r.get('status') == 'FAIL' or r.get('status') == 'ERROR':
            print(f"  • Test {r['test_num']}: {r['description']}")
            if r.get('issue'):
                print(f"    Issue: {r['issue']}")

if warnings > 0:
    print(f"\n⚠️  {warnings} WARNINGS")
    print("Tests needing review:")
    for r in results_log:
        if r.get('status') == 'WARNING':
            print(f"  • Test {r['test_num']}: {r['description']}")
            if r.get('issue'):
                print(f"    Issue: {r['issue']}")

if failed == 0 and warnings == 0:
    print("\n✅ ALL TESTS PASSED!")
    print("The system correctly handles:")
    print("  • Complex multi-symptom inputs")
    print("  • Ambiguous symptom combinations")
    print("  • Edge cases and single symptoms")
    print("  • Natural language variations")
    print("  • Disease confusion scenarios")
    print("  • Various severity levels")
    print("  • Chronic vs acute presentations")
    print("  • Uncommon symptom patterns")
elif pass_rate >= 80:
    print(f"\n✅ GOOD: {pass_rate:.1f}% pass rate")
    print("Most scenarios handled correctly, some edge cases need refinement")
else:
    print(f"\n⚠️  NEEDS IMPROVEMENT: {pass_rate:.1f}% pass rate")
    print("Several scenarios need attention")

print("\n" + "=" * 100)

# Save detailed results
with open('test_results_comprehensive.json', 'w') as f:
    json.dump(results_log, f, indent=2)
print("Detailed results saved to: test_results_comprehensive.json")
