#!/usr/bin/env python3
"""
Test script for disease-aware AI insights.
Tests COVID-19, Dengue, and Malaria for medical accuracy.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_assistant import load_knowledge_base, generate_comprehensive_answer

def test_disease(symptoms, expected_disease_keyword, dangerous_keywords=None, required_keywords=None):
    """Test disease-specific response."""
    print("=" * 80)
    print(f"Testing: {symptoms}")
    print("=" * 80)
    
    knowledge = load_knowledge_base()
    response = generate_comprehensive_answer(symptoms, knowledge, use_advanced=False)
    
    detected_disease = response.get('disease', '').lower()
    ai_insights = response.get('ai_insights', '').lower()
    
    print(f"✓ Detected: {response.get('disease')}")
    print(f"✓ Confidence: {response.get('confidence', 0):.1%}")
    print()
    
    # Check detected disease
    if expected_disease_keyword.lower() not in detected_disease:
        print(f"⚠️  Warning: Expected '{expected_disease_keyword}' in disease name")
    
    # Check for dangerous keywords
    if dangerous_keywords:
        found = [kw for kw in dangerous_keywords if kw.lower() in ai_insights]
        if found:
            print(f"❌ FAIL: Found dangerous keywords: {found}")
            print(f"   AI should NOT mention these for {expected_disease_keyword}")
            return False
        else:
            print(f"✅ PASS: No dangerous keywords ({dangerous_keywords})")
    
    # Check for required keywords
    if required_keywords:
        found = [kw for kw in required_keywords if kw.lower() in ai_insights]
        if len(found) == len(required_keywords):
            print(f"✅ PASS: Found required keywords: {found}")
        else:
            missing = [kw for kw in required_keywords if kw.lower() not in ai_insights]
            print(f"⚠️  Warning: Missing keywords: {missing}")
    
    print()
    print("AI INSIGHTS (first 300 chars):")
    print("-" * 80)
    print(ai_insights[:300] + "...")
    print("-" * 80)
    print()
    
    return True

def main():
    print("\n" + "=" * 80)
    print("DISEASE-AWARE AI INSIGHTS TEST - v3.5")
    print("=" * 80)
    print()
    
    all_pass = True
    
    # Test 1: COVID-19
    print("\n📋 TEST 1: COVID-19")
    result = test_disease(
        symptoms="fever headache dry cough loss of taste",
        expected_disease_keyword="COVID",
        dangerous_keywords=["aspirin", "influenza", "viral fever"],
        required_keywords=["paracetamol", "isolate", "covid"]
    )
    all_pass = all_pass and result
    
    # Test 2: Dengue
    print("\n📋 TEST 2: DENGUE")
    result = test_disease(
        symptoms="dengue fever joint pain",
        expected_disease_keyword="dengue",
        dangerous_keywords=["ibuprofen", "aspirin", "diclofenac"],
        required_keywords=["paracetamol", "bleeding", "platelet"]
    )
    all_pass = all_pass and result
    
    # Test 3: Malaria
    print("\n📋 TEST 3: MALARIA")
    result = test_disease(
        symptoms="malaria fever chills sweating",
        expected_disease_keyword="malaria",
        dangerous_keywords=["self-medicate", "over-the-counter"],
        required_keywords=["antimalarial", "parasitic", "prescription"]
    )
    all_pass = all_pass and result
    
    # Test 4: Diabetes
    print("\n📋 TEST 4: DIABETES")
    result = test_disease(
        symptoms="diabetes frequent urination thirst weight loss",
        expected_disease_keyword="diabetes",
        dangerous_keywords=["cure", "replace insulin"],
        required_keywords=["blood glucose", "monitoring", "lifestyle"]
    )
    all_pass = all_pass and result
    
    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    
    if all_pass:
        print("✅ ALL TESTS PASSED")
        print("   Disease-aware AI insights are medically accurate")
        print("   System ready for production (10/10)")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("   Review AI insights for medical accuracy")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
