#!/usr/bin/env python3
"""
Quick test to verify herbal and pharma recommendations are working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer, format_answer_for_display

print("=" * 70)
print("Testing Herbal & Pharma Recommendations")
print("=" * 70)
print()

# Load knowledge base
print("Loading knowledge base...")
knowledge = load_knowledge_base()
print("✅ Knowledge base loaded")
print()

# Test symptoms
test_symptoms = "fever headache body ache"
print(f"Test symptoms: {test_symptoms}")
print()

# Generate answer
print("Generating comprehensive answer...")
response = generate_comprehensive_answer(
    test_symptoms,
    knowledge,
    use_ai=False,
    include_drugs=True
)
print("✅ Response generated")
print()

# Check what's in the response
print("=" * 70)
print("RESPONSE CONTENTS:")
print("=" * 70)
print(f"Detected Disease: {response.get('detected_disease')}")
print(f"Confidence: {response.get('confidence')}")
print(f"Herbal Recommendations: {len(response.get('herbal_recommendations', []))} items")
print(f"Drug Recommendations: {len(response.get('drug_recommendations', []))} items")
print()

# Show herbal recommendations
if response.get('herbal_recommendations'):
    print("HERBAL RECOMMENDATIONS:")
    for i, rec in enumerate(response['herbal_recommendations'][:3], 1):
        print(f"  {i}. {rec.get('ingredient')} - {rec.get('relevance_score', 0):.2%}")
        print(f"     Benefits: {rec.get('benefits', 'N/A')[:60]}...")
print()

# Show drug recommendations
if response.get('drug_recommendations'):
    print("DRUG RECOMMENDATIONS:")
    for i, drug in enumerate(response['drug_recommendations'][:3], 1):
        print(f"  {i}. {drug.get('name')} - {drug.get('type', 'N/A')}")
        print(f"     Purpose: {drug.get('purpose', 'N/A')[:60]}...")
print()

# Test formatted output
print("=" * 70)
print("FORMATTED OUTPUT:")
print("=" * 70)
formatted = format_answer_for_display(response)
print(formatted)
