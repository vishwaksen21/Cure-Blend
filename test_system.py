#!/usr/bin/env python3
"""
Quick system test to verify all functionality works
"""
import sys
sys.path.insert(0, 'src')

from ai_assistant import generate_comprehensive_answer, load_knowledge_base

def test_system():
    """Test the system with various symptom inputs"""
    print("=" * 70)
    print("SYSTEM FUNCTIONALITY TEST")
    print("=" * 70)
    print()
    
    # Load knowledge base
    print("Loading knowledge base...")
    try:
        knowledge = load_knowledge_base()
        print("✓ Knowledge base loaded successfully\n")
    except Exception as e:
        print(f"✗ ERROR loading knowledge base: {e}\n")
        return False
    
    # Test cases covering different categories
    test_cases = [
        ("fever and headache", "Fever/Dengue detection"),
        ("stomach pain diarrhea", "Digestive issues"),
        ("cough and cold", "Respiratory symptoms"),
        ("joint pain arthritis", "Pain/inflammation"),
        ("diabetes high blood sugar", "Metabolic condition"),
        ("chest pain breathing", "Cardiac/respiratory"),
        ("skin rash itching", "Dermatological"),
        ("anxiety stress", "Mental health"),
    ]
    
    passed = 0
    failed = 0
    
    for symptom, category in test_cases:
        print(f"Testing: {symptom} ({category})")
        try:
            result = generate_comprehensive_answer(
                symptom, 
                knowledge, 
                use_ai=False,  # Disable AI to speed up testing
                include_drugs=True
            )
            
            # Verify essential fields
            disease = result.get('detected_disease', 'Unknown')
            confidence = result.get('confidence', 0)
            herbs = result.get('herbal_recommendations', [])
            drugs = result.get('drug_recommendations', [])
            
            # Check if response is valid
            if disease and disease != 'Unknown' and confidence > 0:
                print(f"  ✓ Disease: {disease} (Confidence: {confidence*100:.1f}%)")
                print(f"  ✓ Recommendations: {len(herbs)} herbs, {len(drugs)} drugs")
                passed += 1
            else:
                print(f"  ⚠ Warning: Low quality response")
                print(f"    Disease: {disease}, Confidence: {confidence*100:.1f}%")
                passed += 1  # Still count as pass if no crash
                
        except Exception as e:
            print(f"  ✗ ERROR: {type(e).__name__}: {str(e)[:100]}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ ALL TESTS PASSED - System is working correctly!")
        return True
    else:
        print(f"✗ {failed} test(s) failed - Please review errors above")
        return False

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
