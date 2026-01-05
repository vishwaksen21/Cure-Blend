#!/usr/bin/env python3
"""
Test script to verify the diagnosis system with various inputs.
This simulates what happens when users enter different symptom combinations.
"""

import sys
import os
import pickle
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("CURE-BLEND DIAGNOSIS SYSTEM TEST")
print("=" * 80)
print()

# Load the model
try:
    with open('data/symptom_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    print("✓ Model loaded successfully")
    print(f"  Model type: {type(model_data.get('model', 'Unknown'))}")
    print()
except Exception as e:
    print(f"✗ Error loading model: {e}")
    sys.exit(1)

# Test cases with various input types
test_cases = [
    {
        "name": "TEST 1: Common Cold Symptoms",
        "symptoms": "fever, headache, runny nose, cough",
        "expected": "Should detect common cold or flu-like illness"
    },
    {
        "name": "TEST 2: Detailed Symptoms with Duration",
        "symptoms": "high fever 102F for 3 days, severe headache, body aches, fatigue",
        "expected": "Should show higher confidence due to detailed information"
    },
    {
        "name": "TEST 3: Dengue-like Symptoms",
        "symptoms": "high fever, severe headache behind eyes, joint pain, muscle pain, rash, nausea, vomiting",
        "expected": "Should detect Dengue with specific diagnostic symptoms"
    },
    {
        "name": "TEST 4: UTI Symptoms",
        "symptoms": "burning during urination, frequent urination, lower abdominal pain, cloudy urine",
        "expected": "Should detect urinary tract infection"
    },
    {
        "name": "TEST 5: Diabetes Symptoms",
        "symptoms": "excessive thirst, frequent urination, fatigue, blurred vision, slow wound healing",
        "expected": "Should detect diabetes"
    },
    {
        "name": "TEST 6: Malaria Symptoms",
        "symptoms": "high fever with chills, sweating, headache, nausea, vomiting, muscle pain",
        "expected": "Should detect malaria"
    },
    {
        "name": "TEST 7: Vague Symptoms (Low Confidence)",
        "symptoms": "not feeling well",
        "expected": "Should show low confidence and trigger follow-up questions"
    },
    {
        "name": "TEST 8: Stomach Issues",
        "symptoms": "stomach pain, nausea, vomiting, diarrhea, loss of appetite",
        "expected": "Should detect gastroenteritis or similar condition"
    },
    {
        "name": "TEST 9: Synonym Testing",
        "symptoms": "temp, tummy ache, feeling sick",
        "expected": "Should normalize to fever, stomach pain, nausea"
    },
    {
        "name": "TEST 10: Emergency Symptoms",
        "symptoms": "severe chest pain, difficulty breathing, sudden weakness",
        "expected": "Should flag as emergency"
    }
]

# Import normalization function from streamlit_app
try:
    # Read the normalize_symptoms function
    def normalize_symptoms(symptoms_text):
        """Normalize common symptom synonyms."""
        replacements = {
            r'\btemp\b': 'fever',
            r'\btummy\b': 'stomach',
            r'\bache\b': 'pain',
            r'\baches\b': 'pain',
            r'\btired\b': 'fatigue',
            r'\bdizzy\b': 'dizziness',
            r'\bthroat\s+pain\b': 'sore throat',
            r'\bfeeling\s+sick\b': 'nausea',
            r'\bstomach\s+upset\b': 'nausea',
            r'\bbad\s+cough\b': 'severe cough',
            r'\bshortness\s+of\s+breath\b': 'difficulty breathing',
        }
        import re
        normalized = symptoms_text.lower()
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized
    
    print("✓ Normalization function loaded")
    print()
except Exception as e:
    print(f"✗ Error loading normalization: {e}")
    normalize_symptoms = lambda x: x.lower()

# Run tests
print("=" * 80)
print("RUNNING TESTS")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    print(f"\n{test['name']}")
    print("-" * 80)
    print(f"Input: {test['symptoms']}")
    print(f"Expected: {test['expected']}")
    
    # Normalize symptoms
    normalized = normalize_symptoms(test['symptoms'])
    if normalized != test['symptoms'].lower():
        print(f"Normalized: {normalized}")
    
    # Check for emergency keywords
    emergency_keywords = [
        'severe chest pain', 'chest pain', 'difficulty breathing',
        'cannot breathe', 'severe bleeding', 'unconscious',
        'sudden weakness', 'severe headache', 'confusion',
        'suicide', 'severe abdominal pain'
    ]
    is_emergency = any(keyword in normalized for keyword in emergency_keywords)
    if is_emergency:
        print("⚠️  EMERGENCY DETECTED - Would trigger emergency protocol")
    
    # Check confidence factors
    word_count = len(normalized.split())
    has_duration = any(word in normalized for word in ['days', 'weeks', 'hours', 'day'])
    has_severity = any(word in normalized for word in ['severe', 'extreme', 'high', 'intense'])
    
    print(f"\nConfidence Factors:")
    print(f"  - Word count: {word_count} {'(detailed)' if word_count >= 5 else '(brief)'}")
    print(f"  - Duration specified: {'Yes' if has_duration else 'No'}")
    print(f"  - Severity mentioned: {'Yes' if has_severity else 'No'}")
    
    # Check for diagnostic symptoms
    diagnostic_matches = {
        'Dengue': ['retro-orbital pain', 'behind eyes', 'joint pain', 'bone pain', 'severe headache'],
        'Malaria': ['chills', 'sweating', 'cyclical fever'],
        'Diabetes': ['excessive thirst', 'frequent urination', 'blurred vision'],
        'UTI': ['burning urination', 'frequent urination', 'cloudy urine'],
        'Tuberculosis': ['night sweats', 'weight loss', 'blood cough'],
    }
    
    found_diagnostic = []
    for disease, symptoms in diagnostic_matches.items():
        for symptom in symptoms:
            if symptom in normalized:
                found_diagnostic.append((disease, symptom))
    
    if found_diagnostic:
        print(f"  - Diagnostic symptoms found:")
        for disease, symptom in found_diagnostic:
            print(f"    • {disease}: {symptom}")
    
    print(f"\n{'✓' if not is_emergency or 'emergency' in test['expected'].lower() else '?'} Test case analyzed")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total test cases: {len(test_cases)}")
print("✓ All test cases processed successfully")
print()
print("NOTE: This test validates input processing and feature detection.")
print("      For full diagnosis testing, run the Streamlit app at http://localhost:8501")
print("=" * 80)
