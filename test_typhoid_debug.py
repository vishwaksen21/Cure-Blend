#!/usr/bin/env python3
"""
Debug Typhoid detection
"""

import sys
sys.path.insert(0, '/workspaces/Cure-Blend')

from src.ai_assistant import detect_condition_v2

# Test 16 input
test_input = "high fever, vomiting, diarrhea, abdominal pain, weakness"

condition, confidence = detect_condition_v2(test_input)

print(f"Input: {test_input}")
print(f"Detected: {condition}")
print(f"Confidence: {confidence*100:.1f}%")
print()

# Let's trace the scoring manually
text = test_input.lower()

# Typhoid score calculation
typhoid_keywords = {
    "typhoid": 3.5, "typhoid fever": 4.0, "enteric fever": 3.5,
    "high fever": 2.0, "prolonged fever": 2.5, "sustained fever": 2.5,
    "fever for": 1.5, "fever that lasts": 2.0,
    "abdominal pain": 2.5, "stomach pain": 2.0, "belly pain": 2.0,
    "constipation": 2.0, "diarrhea": 2.0, "loose stool": 1.5,
    "vomiting": 2.0, "nausea": 1.5,
    "rose spots": 3.0, "weakness": 1.5, "fatigue": 1.0,
    "loss of appetite": 2.0, "headache": 1.0
}

typhoid_score = sum(typhoid_keywords.get(kw, 0) for kw in typhoid_keywords if kw in text)
has_sustained_fever = any(kw in text for kw in ["high fever", "prolonged fever", "sustained fever", "fever for"])
has_gi = any(kw in text for kw in ["abdominal pain", "stomach pain", "vomiting", "diarrhea"])
has_weakness = any(kw in text for kw in ["weakness", "fatigue", "loss of appetite"])

print("=== TYPHOID SCORING ===")
print(f"Base score: {typhoid_score}")
print(f"Has sustained fever: {has_sustained_fever}")
print(f"Has GI symptoms: {has_gi}")  
print(f"Has weakness: {has_weakness}")
if has_sustained_fever and has_gi and has_weakness:
    print(f"With 1.5x boost: {typhoid_score * 1.5}")
print()

# Gastroenteritis score
gastro_keywords = {
    "gastroenteritis": 4.0, "gastritis": 3.5,
    "stomach pain": 2.5, "abdominal pain": 2.5, "nausea": 2.0,
    "vomiting": 2.5, "diarrhea": 2.5, "food poisoning": 3.0,
    "loose stool": 2.0, "stomach upset": 2.0, "indigestion": 1.5
}

gastro_score = sum(gastro_keywords.get(kw, 0) for kw in gastro_keywords if kw in text)

print("=== GASTROENTERITIS SCORING ===")
print(f"Base score: {gastro_score}")
print()

print(f"Winner: {'Typhoid' if typhoid_score * 1.5 > gastro_score else 'Gastroenteritis'}")
