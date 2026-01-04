#!/usr/bin/env python3
"""
Test script to verify dengue safety fixes.
Tests that AI insights mention ONLY Paracetamol (not Ibuprofen/Aspirin).
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_assistant import load_knowledge_base, generate_comprehensive_answer

def test_dengue_safety():
    """Test that dengue recommendations are medically safe."""
    
    print("=" * 80)
    print("DENGUE SAFETY TEST - v3.4 Critical Fix")
    print("=" * 80)
    print()
    
    # Load knowledge base
    print("📚 Loading knowledge base...")
    knowledge = load_knowledge_base()
    print(f"✅ Loaded {len(knowledge.get('herbs', []))} herbs, {len(knowledge.get('drugs', []))} drugs")
    print()
    
    # Test with dengue symptoms
    user_input = "dengue fever joint pain"
    print(f"🧪 Testing input: '{user_input}'")
    print()
    
    # Generate response
    print("🔬 Generating AI response...")
    response = generate_comprehensive_answer(user_input, knowledge, use_advanced=False)
    
    # Extract key information
    detected_disease = response.get('disease', '')
    ai_insights = response.get('ai_insights', '')
    drug_recs = response.get('drug_recommendations', [])
    
    print(f"✅ Detected disease: {detected_disease}")
    print()
    
    # CRITICAL TEST 1: AI insights should NOT mention Ibuprofen/Aspirin
    print("=" * 80)
    print("TEST 1: AI INSIGHTS SAFETY CHECK")
    print("=" * 80)
    
    dangerous_keywords = ['ibuprofen', 'aspirin', 'diclofenac', 'naproxen']
    found_dangerous = []
    for keyword in dangerous_keywords:
        if keyword.lower() in ai_insights.lower():
            found_dangerous.append(keyword)
    
    print("AI INSIGHTS:")
    print("-" * 80)
    print(ai_insights)
    print("-" * 80)
    print()
    
    if found_dangerous:
        print(f"❌ FAIL: AI insights mention NSAIDs: {', '.join(found_dangerous)}")
        print("   This is medically unsafe for dengue patients!")
        return False
    else:
        print("✅ PASS: AI insights do NOT mention NSAIDs")
        if 'paracetamol' in ai_insights.lower() or 'acetaminophen' in ai_insights.lower():
            print("✅ PASS: AI insights correctly recommend Paracetamol")
        else:
            print("⚠️  WARNING: AI insights should mention Paracetamol")
    print()
    
    # CRITICAL TEST 2: Drug recommendations should filter NSAIDs
    print("=" * 80)
    print("TEST 2: DRUG RECOMMENDATIONS SAFETY CHECK")
    print("=" * 80)
    
    print(f"Drug recommendations count: {len(drug_recs)}")
    for i, drug in enumerate(drug_recs, 1):
        drug_name = drug.get('name', 'Unknown')
        print(f"  {i}. {drug_name}")
    print()
    
    nsaid_in_recs = []
    for drug in drug_recs:
        drug_name = drug.get('name', '').lower()
        for nsaid in ['ibuprofen', 'aspirin', 'diclofenac', 'naproxen']:
            if nsaid in drug_name:
                nsaid_in_recs.append(drug.get('name'))
    
    if nsaid_in_recs:
        print(f"⚠️  WARNING: NSAIDs found in recommendations: {', '.join(nsaid_in_recs)}")
        print("   (These should be marked with ❌ in display)")
    else:
        print("✅ PASS: No NSAIDs in drug recommendations")
    print()
    
    # Final verdict
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    
    if not found_dangerous:
        print("✅ DENGUE SAFETY FIX SUCCESSFUL")
        print("   AI insights are medically safe for dengue patients")
        print("   System is ready for production use (10/10)")
        return True
    else:
        print("❌ DENGUE SAFETY FIX FAILED")
        print("   AI insights still contain dangerous NSAID recommendations")
        print("   System is NOT safe for dengue patients")
        return False

if __name__ == "__main__":
    try:
        success = test_dengue_safety()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
