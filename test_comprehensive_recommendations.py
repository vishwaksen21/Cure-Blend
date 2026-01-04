#!/usr/bin/env python3
"""
Comprehensive Test for Enhanced Recommendations System
Tests pharmaceutical and herbal recommendations across common conditions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai_assistant import AIAssistant, suggest_drugs_for_disease, suggest_ingredients_for_disease

def test_conditions():
    """Test a wide range of common conditions"""
    
    test_cases = [
        # Respiratory & Throat
        ("Tonsillitis", "Throat & Respiratory"),
        ("throat pain", "Throat & Respiratory"),
        ("Common Cold", "Respiratory"),
        ("cough and fever", "Respiratory"),
        ("Asthma", "Respiratory"),
        ("Bronchitis", "Respiratory"),
        
        # Digestive
        ("stomach pain", "Digestive"),
        ("Gastroenteritis", "Digestive"),
        ("diarrhea", "Digestive"),
        ("GERD", "Digestive"),
        ("IBS", "Digestive"),
        ("acidity", "Digestive"),
        
        # Pain & Fever
        ("headache", "Pain"),
        ("fever", "Fever"),
        ("muscle pain", "Pain"),
        ("arthritis", "Pain & Inflammation"),
        ("migraine", "Pain"),
        
        # Chronic Conditions
        ("Diabetes", "Chronic"),
        ("Hypertension", "Chronic"),
        
        # Skin
        ("skin rash", "Skin"),
        ("eczema", "Skin"),
        ("fungal infection", "Skin"),
        
        # Infections
        ("UTI", "Infection"),
        ("bacterial infection", "Infection"),
        
        # Mental Health
        ("anxiety", "Mental Health"),
        ("insomnia", "Sleep"),
        
        # General
        ("General Condition", "General"),
        ("fatigue", "General"),
        ("weak immunity", "Immunity"),
    ]
    
    print("="*80)
    print("🧪 COMPREHENSIVE RECOMMENDATIONS TEST")
    print("="*80)
    print(f"\nTesting {len(test_cases)} common conditions...\n")
    
    passed = 0
    failed = 0
    warnings = 0
    
    ai = AIAssistant()
    
    for condition, category in test_cases:
        print(f"\n{'='*80}")
        print(f"🔍 Condition: {condition} ({category})")
        print(f"{'='*80}")
        
        # Test pharmaceutical recommendations
        print("\n💊 Pharmaceutical Recommendations:")
        drugs = suggest_drugs_for_disease(condition, top_n=5)
        
        if drugs:
            print(f"   ✅ Found {len(drugs)} drugs:")
            for i, drug in enumerate(drugs, 1):
                print(f"      {i}. {drug['name']} ({drug['type']})")
                print(f"         Purpose: {drug['purpose']}")
                print(f"         Availability: {drug['availability']} | Price: {drug['price_range']}")
            passed += 1
        else:
            print(f"   ❌ NO PHARMACEUTICAL RECOMMENDATIONS")
            failed += 1
        
        # Test herbal recommendations
        print("\n🌿 Herbal Recommendations:")
        herbs = suggest_ingredients_for_disease(condition)
        
        if herbs:
            print(f"   ✅ Found {len(herbs)} herbs:")
            for i, (herb, score) in enumerate(herbs, 1):
                print(f"      {i}. {herb} (Relevance: {score:.0%})")
            if passed > failed:
                passed += 1
        else:
            print(f"   ⚠️  NO HERBAL RECOMMENDATIONS")
            warnings += 1
        
        # Check if at least one recommendation type exists
        if not drugs and not herbs:
            print("\n   ⛔ CRITICAL: No recommendations at all!")
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Total Conditions Tested: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Comprehensive coverage achieved.")
    elif failed < 5:
        print("\n✅ MOSTLY SUCCESSFUL - Minor improvements needed.")
    else:
        print("\n⚠️  NEEDS IMPROVEMENT - Some conditions lack proper recommendations.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_conditions()
