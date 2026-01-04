#!/usr/bin/env python3
"""Quick test to verify pharmaceutical recommendations are generated"""

import sys
sys.path.insert(0, '/workspaces/Cure-Blend')

from src.ai_assistant import AIAssistant

# Test cases
test_cases = [
    "General Condition",
    "Tonsillitis",
    "throat pain",
    "Unknown Disease"
]

ai = AIAssistant()

print("="*60)
print("TESTING PHARMACEUTICAL RECOMMENDATIONS")
print("="*60)

for disease in test_cases:
    print(f"\n>>> Testing: {disease}")
    drugs = ai.suggest_drugs_for_disease(disease, top_n=5)
    print(f"    Found {len(drugs)} drugs:")
    for drug in drugs:
        print(f"    - {drug.get('name')} ({drug.get('type')})")
    print()

print("="*60)
print("TEST COMPLETE")
print("="*60)
