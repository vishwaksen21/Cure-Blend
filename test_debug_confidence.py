#!/usr/bin/env python3
"""Debug confidence caps"""

import sys
sys.path.insert(0, '/workspaces/Cure-Blend')

from src.ai_assistant import detect_condition_v2

test_cases = [
    ("fever, cough, body ache, fatigue", "Test 5", 40),
    ("chest pain, shortness of breath, dizziness", "Test 6", 40),
    ("stomach pain, nausea, loss of appetite", "Test 7", 40),
    ("bleeding from my gums", "Test 10", 40),
    ("fever, cough, difficulty breathing, chest pain", "Test 17", 40),
    ("joint pain, muscle pain, fatigue, no fever", "Test 18", 35),
    ("fever but no cough, no cold symptoms", "Test 27", 25),
    ("high fever without any rash or bleeding", "Test 28", 30),
]

for input_text, test_name, max_expected in test_cases:
    condition, confidence = detect_condition_v2(input_text)
    conf_pct = confidence * 100
    status = "✓" if conf_pct <= max_expected else "✗"
    print(f"{status} {test_name}: {condition} = {conf_pct:.1f}% (max: {max_expected}%)")
