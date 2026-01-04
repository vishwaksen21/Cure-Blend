#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspaces/Cure-Blend')

from src.ai_assistant import suggest_drugs_for_disease

print("Testing drug recommendations...")
print("="*60)

# Test with different disease names
tests = [
    "General Condition",
    "Tonsillitis",
    "throat pain",
    "sore throat"
]

for disease in tests:
    print(f"\nTest: '{disease}'")
    drugs = suggest_drugs_for_disease(disease, top_n=5)
    print(f"  Results: {len(drugs)} drugs")
    for i, d in enumerate(drugs[:3], 1):
        print(f"    {i}. {d.get('name')} - {d.get('type')}")

print("\n" + "="*60)
print("If you see 5 drugs for each test, it's working!")
