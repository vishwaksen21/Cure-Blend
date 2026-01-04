#!/usr/bin/env python3
"""
Simple verification that recommendations are working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("🔍 VERIFICATION: Herbal & Pharma Recommendations")
print("="*70 + "\n")

try:
    from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer
    
    print("✅ Imports successful")
    print("⏳ Loading knowledge base...")
    
    kb = load_knowledge_base()
    print("✅ Knowledge base loaded")
    
    print("⏳ Testing with sample symptoms...")
    
    response = generate_comprehensive_answer(
        "fever headache body ache",
        kb,
        use_ai=False,
        include_drugs=True
    )
    
    print("✅ Response generated\n")
    
    # Check response
    herbal_count = len(response.get('herbal_recommendations', []))
    drug_count = len(response.get('drug_recommendations', []))
    
    print("="*70)
    print("RESULTS:")
    print("="*70)
    print(f"Disease:  {response.get('detected_disease', 'N/A')}")
    print(f"Confidence: {response.get('confidence', 0)*100:.1f}%")
    print(f"\n🌿 Herbal recommendations: {herbal_count}")
    print(f"💊 Drug recommendations:    {drug_count}")
    print("="*70)
    
    if herbal_count > 0 and drug_count > 0:
        print("\n✅ ✅ ✅ SUCCESS! Both recommendations are working! ✅ ✅ ✅\n")
        print("Sample herbal:")
        for h in response['herbal_recommendations'][:2]:
            print(f"  • {h.get('ingredient')}")
        print("\nSample drugs:")
        for d in response['drug_recommendations'][:2]:
            print(f"  • {d.get('name')}")
        print("\n" + "="*70)
        print("👍 You can now run: python3 main.py")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n⚠️  WARNING: Some recommendations are missing!")
        print(f"   Herbal: {herbal_count}, Drugs: {drug_count}")
        print("\n💡 Check:")
        print("   1. Data files in data/ directory")
        print("   2. Run: python3 setup_complete_datasets.py")
        print("="*70 + "\n")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
    import traceback
    traceback.print_exc()
    print("\n💡 Try:")
    print("   pip install -r requirements.txt")
    print("="*70 + "\n")
    sys.exit(1)
