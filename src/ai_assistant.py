#!/usr/bin/env python3
"""
Max-Expanded Standalone Terminal AI Health Assistant
- Combines herbal suggestions + pharmaceutical suggestions
- Large lookup dictionaries and embedded sample data if CSVs missing
- Keeps original logic intact; adds robustness, logging, TTS, and AI-insight fallback
"""

import os
import sys
import json
import time
import math
import datetime
from typing import Dict, List, Tuple, Set

# Optional imports; handle gracefully
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import numpy as np
except Exception:
    np = None

# gensim / joblib optional for embeddings-based suggestions (kept but handled)
try:
    from gensim.models import KeyedVectors
except Exception:
    KeyedVectors = None

try:
    import joblib
except Exception:
    joblib = None

# Try to import pyttsx3 for TTS (optional)
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    pyttsx3 = None
    TTS_AVAILABLE = False

# Try to import Azure LLM client (optional)
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential
    HAS_LLM = True
except Exception:
    HAS_LLM = False

# Try to import dataset integrator (optional)
try:
    from .dataset_integration import get_integrator
    HAS_INTEGRATOR = True
except Exception:
    try:
        from dataset_integration import get_integrator
        HAS_INTEGRATOR = True
    except Exception:
        HAS_INTEGRATOR = False

# Preserve your import logic for symptom predictors and drug DB (fallback safe)
USE_ENHANCED = False
try:
    from .enhanced_symptom_predictor import predict_disease_enhanced
    USE_ENHANCED = True
except Exception:
    try:
        from enhanced_symptom_predictor import predict_disease_enhanced
        USE_ENHANCED = True
    except Exception:
        try:
            from .symptom_predictor import predict_disease
            USE_ENHANCED = False
        except Exception:
            try:
                from symptom_predictor import predict_disease
            except Exception:
                # Fallback simple predictor if module missing
                def predict_disease(text: str):
                    # Very simple heuristic fallback (keyword match)
                    text_l = (text or "").lower()
                    if any(k in text_l for k in ["cough", "sore throat", "runny", "congest"]):
                        return "Common Cold", 0.6
                    if any(k in text_l for k in ["fever", "chills", "rigor"]):
                        return "Fever", 0.6
                    if any(k in text_l for k in ["headache", "migraine", "throbb"]):
                        return "Headache", 0.6
                    if any(k in text_l for k in ["diarr", "loose motion", "loose stool", "vomit"]):
                        return "Gastroenteritis", 0.75
                    if any(k in text_l for k in ["breath", "wheez", "asthma"]):
                        return "Asthma", 0.6
                    return "General Symptom", 0.5
                USE_ENHANCED = False

# Drug DB fallback flag - attempt import as user original
HAS_DRUG_DB = False
try:
    from .drug_database import DrugDatabase
    HAS_DRUG_DB = True
except Exception:
    try:
        from drug_database import DrugDatabase
        HAS_DRUG_DB = True
    except Exception:
        HAS_DRUG_DB = False

# ------------------------------------------------------------------------------------
# ENHANCED condition detection (v2) with weighted scoring and multi-symptom support
# ------------------------------------------------------------------------------------
def detect_condition_v2(user_input: str) -> Tuple[str, float]:
    """
    Enhanced disease/condition detection using weighted keyword scoring and multi-symptom analysis.
    
    Returns: (condition_name, confidence_score)
    
    Features:
    - Handles multi-symptom inputs (e.g., "fever with joint pain" → Dengue)
    - Detects reproductive & hormonal cases (PCOS, dysmenorrhea, menorrhagia)
    - Accurate digestive issue classification
    - Respiratory and infection detection
    - Musculoskeletal condition mapping
    - Mental health & neurological cases
    - Cardiac & metabolic issue detection
    - Weighted scoring system prioritizes specific matches over general ones
    """
    text = (user_input or "").lower().strip()
    
    if not text:
        return "No Condition Detected", 0.0
    
    # Initialize scoring dictionary for all possible conditions
    scores = {}
    
    # ─────────────────────────────────────────────────────────────────
    # 1. REPRODUCTIVE & HORMONAL CONDITIONS (Highest specificity)
    # ─────────────────────────────────────────────────────────────────
    
    # PCOS / Hormonal Disorder Detection
    # Added PCOS logic: Enhanced keywords for missed periods, cycle irregularity, and metabolic symptoms
    pcos_keywords = {
        "missed period": 3.5, "missed periods": 3.5, "period stopped": 3.5,
        "no periods": 3.5, "no period": 3.5, "haven't had period": 3.0,
        "irregular cycle": 2.5, "irregular periods": 2.5, "irregular menstrual": 2.5,
        "hair loss": 2.5, "acne": 2.5, "weight gain": 2.5,
        "hormonal": 2.5, "pcos": 4.0, "polycystic": 4.0,
        "facial hair": 2.5, "oily skin": 2.0, "dark patches": 2.0
    }
    hormonal_score = sum(pcos_keywords.get(kw, 0) for kw in pcos_keywords if kw in text)
    # Boost score if multiple PCOS-related symptoms detected (multi-symptom confirmation)
    pcos_symptom_count = sum(1 for kw in pcos_keywords if kw in text)
    if pcos_symptom_count >= 2:
        hormonal_score *= 1.25
    if hormonal_score > 0:
        scores["Hormonal Disorder (Possible PCOS)"] = hormonal_score
    
    # Dysmenorrhea (Period Pain/Cramps)
    # Preserved other mappings: Period pain and cramps detection
    # Added PCOS logic: Suppress Dysmenorrhea if PCOS indicators (missed periods + metabolic symptoms) are present
    dysmenorrhea_keywords = {
        "period pain": 3.5, "period cramp": 3.5, "menstrual cramp": 3.5,
        "cramps": 2.5, "dysmenorrhea": 4.0,
        "pelvic pain": 2.0, "lower abdominal pain": 2.0, "lower belly pain": 2.0,
        "painful periods": 3.5, "pain during period": 3.5
    }
    dysmenorrhea_score = sum(dysmenorrhea_keywords.get(kw, 0) for kw in dysmenorrhea_keywords if kw in text)
    
    # SUPPRESS Dysmenorrhea if PCOS indicators present (missed periods + metabolic symptoms)
    has_pcos_indicators = any(kw in text for kw in ["missed period", "missed periods", "no periods", "no period", "period stopped", "haven't had period"])
    has_pcos_metabolic = any(kw in text for kw in ["hair loss", "acne", "weight gain", "facial hair", "hormonal"])
    if dysmenorrhea_score > 0 and not (has_pcos_indicators and has_pcos_metabolic):
        scores["Dysmenorrhea"] = dysmenorrhea_score
    
    # Menorrhagia (Heavy/Prolonged Menstrual Bleeding)
    # Added Menorrhagia logic: Keywords for heavy bleeding, prolonged flow, and associated weakness/dizziness
    menorrhagia_keywords = {
        "heavy bleeding": 4.0, "heavy menstrual": 3.5, "excessive bleeding": 4.0,
        "prolonged bleeding": 4.0, "bleeding more than a week": 4.0,
        "heavy flow": 3.5, "flooding": 3.0,
        "blood clots": 2.5, "soaking pads": 3.0,
        "weak and dizzy": 3.5, "weakness and dizziness": 3.5, "weak dizzy": 3.5,
        "blood loss": 3.0, "heavy period": 4.0, "heavy periods": 4.0,
        "prolonged period": 3.5, "long period": 3.0,
        "weak": 1.5, "weakness": 1.5, "dizzy": 1.5, "dizziness": 1.5
    }
    menorrhagia_score = sum(menorrhagia_keywords.get(kw, 0) for kw in menorrhagia_keywords if kw in text)
    # Boost score if heavy bleeding symptoms combined with weakness/dizziness
    has_heavy_bleed = any(kw in text for kw in ["heavy bleeding", "heavy flow", "flooding", "prolonged bleeding", "bleeding more than a week"])
    has_weakness = any(kw in text for kw in ["weak", "dizzy", "weakness", "dizziness"])
    if has_heavy_bleed and has_weakness:
        menorrhagia_score *= 1.4
    if menorrhagia_score > 0:
        scores["Menorrhagia"] = menorrhagia_score
    
    # ─────────────────────────────────────────────────────────────────
    # 2. RESPIRATORY & INFECTION CONDITIONS
    # ─────────────────────────────────────────────────────────────────
    
    # Influenza / Viral Fever
    flu_keywords = {
        "fever": 1.5, "high fever": 2.0, "body ache": 2.5, "muscle pain": 2.5,
        "sore throat": 1.5, "cough": 1.0, "cold": 1.0,
        "chills": 2.5, "rigor": 2.5, "fatigue": 1.5, "tired": 1.0,
        "flu": 3.5, "influenza": 3.5, "viral": 2.0
    }
    # Check for multi-symptom combinations
    flu_symptoms = [kw for kw in flu_keywords if kw in text]
    flu_score = sum(flu_keywords.get(kw, 0) for kw in flu_symptoms)
    
    # Only boost/use flu if fever or chills are explicitly mentioned
    has_fever_symptoms = any(kw in text for kw in ["fever", "high fever", "chills", "rigor"])
    if has_fever_symptoms and len(flu_symptoms) >= 2:
        flu_score *= 1.3
    
    if flu_score > 0 and has_fever_symptoms:
        scores["Influenza / Viral Fever"] = flu_score
    
    # Dengue / Viral Fever with Rash
    dengue_keywords = {
        "dengue": 4.0, "dengue fever": 4.0,
        "fever with rash": 3.0, "rash with fever": 3.0,
        "joint pain with fever": 3.0, "fever and joint pain": 3.0,
        "body pain with fever": 2.5, "fever and body ache": 2.5,
        "joint pain": 1.5, "body ache": 1.0, "rash": 2.0,
        "platelet": 2.5, "low platelet": 2.5, "hemorrhagic": 3.0
    }
    dengue_symptoms = [kw for kw in dengue_keywords if kw in text]
    dengue_score = sum(dengue_keywords.get(kw, 0) for kw in dengue_symptoms)
    if len(dengue_symptoms) >= 2:
        dengue_score *= 1.2  # Boost for multi-symptom match
    if dengue_score > 0:
        scores["Dengue / Viral Fever"] = dengue_score
    
    # Common Cold
    cold_keywords = {
        "cold": 2.0, "runny nose": 2.5, "sore throat": 1.5, "cough": 1.0,
        "nasal congestion": 2.0, "stuffy nose": 1.5, "sneeze": 1.5,
        "common cold": 3.0, "nose congestion": 2.0
    }
    cold_score = sum(cold_keywords.get(kw, 0) for kw in cold_keywords if kw in text)
    if cold_score > 0:
        scores["Common Cold / Influenza"] = cold_score
    
    # ─────────────────────────────────────────────────────────────────
    # 3. GASTROINTESTINAL CONDITIONS
    # ─────────────────────────────────────────────────────────────────
    
    # Gastroenteritis / Food Poisoning
    gastro_keywords = {
        "vomiting": 2.5, "diarrhea": 2.5, "diarrhoea": 2.5,
        "loose motion": 2.5, "loose stool": 2.5,
        "stomach pain": 2.0, "stomach ache": 2.0, "abdominal pain": 1.5,
        "food poisoning": 3.0, "gastroenteritis": 3.0,
        "nausea": 1.5, "vomit and diarrhea": 3.5,
        "after eating": 1.0, "stomach upset": 1.5
    }
    gastro_symptoms = [kw for kw in gastro_keywords if kw in text]
    gastro_score = sum(gastro_keywords.get(kw, 0) for kw in gastro_symptoms)
    # Strong indicator if both vomiting AND diarrhea
    if "vomiting" in text and ("diarrhea" in text or "loose motion" in text):
        gastro_score *= 1.4
    if gastro_score > 0:
        scores["Gastroenteritis / Gastritis"] = gastro_score
    
    # Acidity / Acid Reflux / Indigestion
    acidity_keywords = {
        "acidity": 3.0, "acid reflux": 3.0, "gerd": 3.0,
        "indigestion": 2.5, "heartburn": 2.5, "gas": 1.0,
        "bloating": 1.5, "stomach upset": 1.5
    }
    acidity_score = sum(acidity_keywords.get(kw, 0) for kw in acidity_keywords if kw in text)
    if acidity_score > 0:
        scores["Gastritis / Acidity"] = acidity_score
    
    # ─────────────────────────────────────────────────────────────────
    # 4. MUSCULOSKELETAL CONDITIONS
    # ─────────────────────────────────────────────────────────────────
    
    # Arthritis / Joint Pain
    arthritis_keywords = {
        "arthritis": 3.0, "joint pain": 2.0, "joint ache": 2.0,
        "rheumatoid arthritis": 3.5, "osteoarthritis": 3.0,
        "morning stiffness": 2.5, "joint stiffness": 2.0,
        "knee pain": 1.5, "hip pain": 1.5, "ankle pain": 1.5,
        "joint inflammation": 2.5, "swelling in joint": 2.0
    }
    arthritis_symptoms = [kw for kw in arthritis_keywords if kw in text]
    arthritis_score = sum(arthritis_keywords.get(kw, 0) for kw in arthritis_symptoms)
    if arthritis_score > 0:
        scores["Arthritis"] = arthritis_score
    
    # Back Pain / Cervical Spondylosis
    back_pain_keywords = {
        "back pain": 2.5, "backache": 2.5, "lower back pain": 2.5,
        "upper back pain": 2.5, "cervical": 3.0, "cervical spondylosis": 3.0,
        "neck pain": 2.0, "neck strain": 2.0, "neck stiffness": 2.0,
        "spinal pain": 2.5, "sciatica": 3.0, "slipped disc": 3.0
    }
    back_pain_symptoms = [kw for kw in back_pain_keywords if kw in text]
    back_pain_score = sum(back_pain_keywords.get(kw, 0) for kw in back_pain_symptoms)
    if back_pain_score > 0:
        scores["Muscle Strain / Cervical Spondylosis"] = back_pain_score
    
    # Muscle Strain / General Muscle Pain
    muscle_keywords = {
        "muscle pain": 2.0, "muscle ache": 2.0, "muscle strain": 2.5,
        "muscle soreness": 2.0, "muscle cramp": 2.0, "charley horse": 1.5
    }
    muscle_score = sum(muscle_keywords.get(kw, 0) for kw in muscle_keywords if kw in text)
    if muscle_score > 0 and "arthritis" not in scores:
        scores["Muscle Strain"] = muscle_score
    
    # ─────────────────────────────────────────────────────────────────
    # 5. MENTAL HEALTH & NEUROLOGICAL CONDITIONS
    # ─────────────────────────────────────────────────────────────────
    
    # Anxiety Disorder
    anxiety_keywords = {
        "anxiety": 3.0, "anxious": 2.5, "panic": 3.0, "panic attack": 3.0,
        "worried": 1.5, "stress": 1.5, "stressed": 1.5, "nervousness": 2.0,
        "restless": 2.0, "unease": 2.0
    }
    anxiety_score = sum(anxiety_keywords.get(kw, 0) for kw in anxiety_keywords if kw in text)
    if anxiety_score > 0:
        scores["Anxiety Disorder"] = anxiety_score
    
    # Insomnia / Sleep Issues
    sleep_keywords = {
        "insomnia": 3.0, "trouble sleeping": 2.5, "can't sleep": 2.5,
        "unable to sleep": 2.5, "sleepless": 2.5, "waking up at night": 2.0,
        "sleep problem": 2.0, "insomnic": 2.5
    }
    sleep_score = sum(sleep_keywords.get(kw, 0) for kw in sleep_keywords if kw in text)
    if sleep_score > 0:
        scores["Insomnia / Sleep Disorder"] = sleep_score
    
    # Depression / Fatigue / Low Energy
    depression_keywords = {
        "depression": 3.0, "depressed": 2.5, "sad": 2.0, "hopeless": 2.5,
        "low mood": 2.0, "mood swings": 2.0
    }
    depression_score = sum(depression_keywords.get(kw, 0) for kw in depression_keywords if kw in text)
    
    fatigue_keywords = {
        "fatigue": 2.5, "tired": 1.5, "exhausted": 2.0, "weakness": 1.5,
        "weak": 1.0, "lethargy": 2.0, "low energy": 2.0, "worn out": 1.5,
        "fatigued": 2.0
    }
    fatigue_score = sum(fatigue_keywords.get(kw, 0) for kw in fatigue_keywords if kw in text)
    
    # Combine depression + fatigue for fatigue syndrome
    combined_mental = depression_score + fatigue_score
    if combined_mental > 0:
        # If depression keywords present, favor depression
        if depression_score > fatigue_score:
            scores["Depression"] = depression_score
        else:
            scores["Anxiety Disorder / Fatigue Syndrome"] = combined_mental
    
    # ─────────────────────────────────────────────────────────────────
    # 6. CARDIAC & METABOLIC CONDITIONS
    # ─────────────────────────────────────────────────────────────────
    
    # Hypertension / Cardiac Stress
    cardiac_keywords = {
        "high blood pressure": 3.0, "high bp": 3.0, "hypertension": 3.0,
        "chest pain": 3.0, "chest ache": 3.0, "chest tightness": 3.0,
        "heart palpitations": 3.0, "irregular heartbeat": 3.0,
        "shortness of breath": 1.5, "difficulty breathing": 1.5,
        "dizziness": 1.0, "fatigue": 0.5
    }
    cardiac_symptoms = [kw for kw in cardiac_keywords if kw in text]
    cardiac_score = sum(cardiac_keywords.get(kw, 0) for kw in cardiac_symptoms)
    # Boost if multiple cardiac-specific symptoms (not just general breathing)
    if len([s for s in cardiac_symptoms if s in ["high blood pressure", "high bp", "hypertension", "chest pain", "chest ache", "chest tightness", "heart palpitations", "irregular heartbeat"]]) >= 1:
        if cardiac_score > 0:
            scores["Hypertension / Cardiac Stress"] = cardiac_score
    
    # ─────────────────────────────────────────────────────────────────
    # 7. OTHER MAJOR CONDITIONS
    # ─────────────────────────────────────────────────────────────────
    
    # Fever (Generic)
    fever_keywords = {
        "fever": 1.5, "high temperature": 1.5, "high fever": 1.5,
        "feverish": 1.5, "temperature": 1.0, "hot": 0.5
    }
    fever_score = sum(fever_keywords.get(kw, 0) for kw in fever_keywords if kw in text)
    # Only use generic fever if no specific fever condition already scored
    if fever_score > 0 and not any(cond in scores for cond in ["Influenza / Viral Fever", "Dengue / Viral Fever", "Common Cold / Influenza"]):
        scores["Fever"] = fever_score
    
    # Headache / Migraine
    headache_keywords = {
        "headache": 2.0, "head pain": 2.0, "head ache": 2.0,
        "migraine": 3.0, "throbbing": 2.0, "pounding": 2.0,
        "tension headache": 2.5, "cluster headache": 2.5,
        "dizziness": 1.0, "dizziness": 1.0, "vertigo": 1.5
    }
    headache_symptoms = [kw for kw in headache_keywords if kw in text]
    headache_score = sum(headache_keywords.get(kw, 0) for kw in headache_symptoms)
    if headache_score > 0:
        # Prefer migraine if "migraine" or "throbbing" in text
        if "migraine" in text or "throbbing" in text:
            scores["Migraine"] = headache_score
        else:
            scores["Headache"] = headache_score
    
    # Asthma & Respiratory Issues
    asthma_keywords = {
        "asthma": 3.0, "asthmatic": 2.5, "wheeze": 3.0, "wheezing": 3.0,
        "shortness of breath": 2.0, "breathing difficulty": 2.5, "difficulty breathing": 2.5,
        "bronchitis": 2.5, "bronchial": 2.0
    }
    asthma_score = sum(asthma_keywords.get(kw, 0) for kw in asthma_keywords if kw in text)
    if asthma_score > 0:
        scores["Asthma / Bronchitis"] = asthma_score
    
    # Diabetes
    diabetes_keywords = {
        "diabetes": 3.0, "diabetic": 2.5, "blood sugar": 2.5,
        "glucose": 2.0, "hyperglycemia": 3.0, "high sugar": 2.5
    }
    diabetes_score = sum(diabetes_keywords.get(kw, 0) for kw in diabetes_keywords if kw in text)
    if diabetes_score > 0:
        scores["Diabetes"] = diabetes_score
    
    # UTI (Urinary Tract Infection)
    uti_keywords = {
        "uti": 3.0, "urinary tract": 3.0, "urinary tract infection": 3.0,
        "painful urination": 2.5, "dysuria": 2.5, "urination pain": 2.5,
        "bladder infection": 3.0, "kidney infection": 2.5,
        "urination": 1.0
    }
    uti_score = sum(uti_keywords.get(kw, 0) for kw in uti_keywords if kw in text)
    if uti_score > 0:
        scores["Urinary Tract Infection (UTI)"] = uti_score
    
    # Malaria
    malaria_keywords = {
        "malaria": 3.5, "malarial": 3.0, "intermittent fever": 2.5,
        "chills with fever": 2.5
    }
    malaria_score = sum(malaria_keywords.get(kw, 0) for kw in malaria_keywords if kw in text)
    if malaria_score > 0:
        scores["Malaria"] = malaria_score
    
    # ─────────────────────────────────────────────────────────────────
    # DETERMINE FINAL RESULT
    # ─────────────────────────────────────────────────────────────────
    
    if not scores:
        # No specific keywords matched
        return "General Condition", 0.50
    
    # Find condition with highest score
    best_condition = max(scores, key=scores.get)
    best_score = scores[best_condition]
    
    # Normalize score to confidence (0-1 range)
    # Max possible score is roughly 20, use sigmoid-like normalization
    confidence = min(0.95, best_score / 10.0)
    
    return best_condition, confidence


# ------------------------------------------------------------------------------------
# Terminal formatting helpers
# ------------------------------------------------------------------------------------
HEADER = "\033[95m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

def speak_text(text: str):
    """Speak using pyttsx3 if available (non-blocking-ish)."""
    if not TTS_AVAILABLE:
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        # silently ignore TTS failures
        pass

# ------------------------------------------------------------------------------------
# Embedded sample data (used if CSV files are missing)
# ------------------------------------------------------------------------------------
# Minimal sample CSV-like data so script runs standalone
SAMPLE_DISEASES = [
    {"disease": "Gastroenteritis", "symptom": "Diarrhea, vomiting, stomach pain"},
    {"disease": "Common Cold", "symptom": "Runny nose, sore throat, cough"},
    {"disease": "Fever", "symptom": "Raised body temperature, chills"},
    {"disease": "Headache", "symptom": "Pain in head or neck region"},
    {"disease": "Asthma", "symptom": "Wheezing, shortness of breath"},
]

SAMPLE_HERBS = [
    {"herb": "Ginger", "benefits": "Anti-nausea, anti-inflammatory", "active_compounds": "Gingerols", "usage": "Ginger tea 1-2 cups daily"},
    {"herb": "Peppermint", "benefits": "Soothes stomach, relieves gas", "active_compounds": "Menthol", "usage": "Peppermint infusion as needed"},
    {"herb": "Turmeric", "benefits": "Anti-inflammatory", "active_compounds": "Curcumin", "usage": "250-500 mg with meals"},
    {"herb": "Neem", "benefits": "Antimicrobial", "active_compounds": "Azadirachtin", "usage": "Topical or decoction by expert"},
    {"herb": "Clove", "benefits": "Analgesic and antimicrobial", "active_compounds": "Eugenol", "usage": "Use in small amounts"}
]

SAMPLE_INGREDIENTS = [
    {"ingredient": "Ginger", "target": "Gastroenteritis"},
    {"ingredient": "Turmeric", "target": "Inflammation"},
    {"ingredient": "Eugenol", "target": "Pain"},
    {"ingredient": "Withaferin A", "target": "Immune Support"},
]

SAMPLE_TARGETS = [
    {"target": "Gastroenteritis", "disease": "Gastroenteritis"},
    {"target": "A Common Cold", "disease": "Common Cold"},
    {"target": "Fever", "disease": "Fever"},
]

SAMPLE_DRUGS = [
    # Pain & Fever Relief (Comprehensive)
    {"name": "Paracetamol", "brand_names": ["Crocin", "Panadol", "Dolo"], "type": "Analgesic/Antipyretic", "dosage": "500-1000 mg every 4-6h", "purpose": "Reduce fever and pain", "availability": "OTC", "price_range": "₹5-50", "side_effects": "Liver toxicity in overdose"},
    {"name": "Ibuprofen", "brand_names": ["Brufen", "Advil", "Combiflam"], "type": "NSAID", "dosage": "200-400 mg every 6-8h", "purpose": "Reduce pain, inflammation and fever", "availability": "OTC", "price_range": "₹10-80", "side_effects": "GI upset, ulcers with long-term use"},
    {"name": "Aspirin", "brand_names": ["Disprin", "Ecosprin"], "type": "NSAID", "dosage": "300-600 mg every 4-6h", "purpose": "Pain, fever, inflammation, blood thinning", "availability": "OTC", "price_range": "₹5-40", "side_effects": "GI bleeding, avoid in children"},
    {"name": "Diclofenac", "brand_names": ["Voveran", "Voltaren"], "type": "NSAID", "dosage": "50 mg three times daily", "purpose": "Severe pain, arthritis, muscle strain", "availability": "Prescription", "price_range": "₹15-100", "side_effects": "GI upset, cardiovascular risk"},
    
    # Throat & Respiratory (Expanded)
    {"name": "Amoxicillin", "brand_names": ["Amoxil", "Mox"], "type": "Antibiotic", "dosage": "500 mg three times daily", "purpose": "Bacterial infections including throat and respiratory", "availability": "Prescription", "price_range": "₹30-150", "side_effects": "Diarrhea, rash, allergic reactions"},
    {"name": "Azithromycin", "brand_names": ["Azithral", "Zithromax"], "type": "Antibiotic", "dosage": "500 mg once daily for 3 days", "purpose": "Respiratory and throat infections", "availability": "Prescription", "price_range": "₹50-200", "side_effects": "Nausea, diarrhea"},
    {"name": "Lozenges", "brand_names": ["Strepsils", "Vicks", "Cofsils"], "type": "Throat Lozenge", "dosage": "1 lozenge every 2-3h", "purpose": "Soothe throat pain and irritation", "availability": "OTC", "price_range": "₹20-100", "side_effects": "Minimal - avoid excessive use"},
    {"name": "Betadine Gargle", "brand_names": ["Betadine"], "type": "Antiseptic", "dosage": "Gargle 3-4 times daily", "purpose": "Throat infection, tonsillitis, pharyngitis", "availability": "OTC", "price_range": "₹50-150", "side_effects": "Temporary staining, avoid if iodine allergy"},
    {"name": "Chlorpheniramine", "brand_names": ["Avil", "Chlor-Trimeton"], "type": "Antihistamine", "dosage": "4 mg every 4-6h", "purpose": "Relieve allergy symptoms, runny nose, sneezing", "availability": "OTC", "price_range": "₹10-50", "side_effects": "Drowsiness, dry mouth"},
    
    # Cough & Cold (Comprehensive)
    {"name": "Dextromethorphan", "brand_names": ["Benadryl", "Robitussin"], "type": "Cough Suppressant", "dosage": "10-20 mg every 4h", "purpose": "Suppress dry cough", "availability": "OTC", "price_range": "₹50-150", "side_effects": "Drowsiness, dizziness"},
    {"name": "Guaifenesin", "brand_names": ["Mucinex"], "type": "Expectorant", "dosage": "200-400 mg every 4h", "purpose": "Loosen mucus and phlegm", "availability": "OTC", "price_range": "₹40-120", "side_effects": "Nausea, vomiting, dizziness"},
    {"name": "Cetirizine", "brand_names": ["Zyrtec", "Alerid"], "type": "Antihistamine", "dosage": "10 mg once daily", "purpose": "Allergy relief, cold symptoms, runny nose", "availability": "OTC", "price_range": "₹15-80", "side_effects": "Minimal drowsiness"},
    {"name": "Pseudoephedrine", "brand_names": ["Sudafed", "Sinarest"], "type": "Decongestant", "dosage": "30-60 mg every 4-6h", "purpose": "Nasal congestion, sinus pressure", "availability": "OTC", "price_range": "₹40-120", "side_effects": "Insomnia, nervousness, increased BP"},
    {"name": "Salbutamol", "brand_names": ["Asthalin", "Ventolin"], "type": "Bronchodilator", "dosage": "2 puffs every 4-6h", "purpose": "Asthma, bronchitis, breathing difficulty", "availability": "Prescription", "price_range": "₹80-250", "side_effects": "Tremors, palpitations"},
    
    # Digestive (Comprehensive)
    {"name": "Omeprazole", "brand_names": ["Prilosec", "Omez"], "type": "Proton pump inhibitor", "dosage": "20-40 mg daily", "purpose": "Reduce stomach acid, treat GERD and ulcers", "availability": "Prescription", "price_range": "₹40-200", "side_effects": "Headache, nausea"},
    {"name": "Ranitidine", "brand_names": ["Zantac", "Aciloc"], "type": "H2 Blocker", "dosage": "150 mg twice daily", "purpose": "Reduce stomach acid and heartburn", "availability": "OTC", "price_range": "₹20-100", "side_effects": "Headache, constipation"},
    {"name": "Antacids", "brand_names": ["Gelusil", "ENO", "Digene"], "type": "Antacid", "dosage": "1-2 tablets as needed", "purpose": "Quick relief from acidity and heartburn", "availability": "OTC", "price_range": "₹10-60", "side_effects": "Constipation or diarrhea"},
    {"name": "Loperamide", "brand_names": ["Imodium", "Lopamide"], "type": "Anti-diarrheal", "dosage": "2-4 mg after each loose stool", "purpose": "Stop diarrhea", "availability": "OTC", "price_range": "₹30-120", "side_effects": "Constipation, dizziness"},
    {"name": "Oral Rehydration Salts", "brand_names": ["ORS", "Electral"], "type": "Oral solution", "dosage": "As directed", "purpose": "Rehydration for diarrhea and vomiting", "availability": "OTC", "price_range": "₹10-50", "side_effects": "None if used correctly"},
    {"name": "Domperidone", "brand_names": ["Motilium", "Domstal"], "type": "Anti-emetic", "dosage": "10 mg three times daily", "purpose": "Relieve nausea and vomiting", "availability": "Prescription", "price_range": "₹20-100", "side_effects": "Dry mouth, headache"},
    {"name": "Mebeverine", "brand_names": ["Colospa"], "type": "Antispasmodic", "dosage": "135 mg three times daily", "purpose": "IBS, abdominal cramps, stomach spasms", "availability": "Prescription", "price_range": "₹50-200", "side_effects": "Dizziness, headache"},
    {"name": "Probiotics", "brand_names": ["Econorm", "Bifilac"], "type": "Probiotic", "dosage": "1 sachet twice daily", "purpose": "Restore gut flora, diarrhea, digestive health", "availability": "OTC", "price_range": "₹100-300", "side_effects": "Minimal - mild gas"},
    
    # Infections & Antibiotics
    {"name": "Ciprofloxacin", "brand_names": ["Ciplox", "Cifran"], "type": "Antibiotic", "dosage": "500 mg twice daily", "purpose": "UTI, kidney infection, bacterial infections", "availability": "Prescription", "price_range": "₹30-150", "side_effects": "Nausea, diarrhea, tendon damage"},
    {"name": "Metronidazole", "brand_names": ["Flagyl"], "type": "Antibiotic", "dosage": "400 mg three times daily", "purpose": "Bacterial and parasitic infections, dental infections", "availability": "Prescription", "price_range": "₹20-100", "side_effects": "Metallic taste, nausea, avoid alcohol"},
    {"name": "Doxycycline", "brand_names": ["Doxy-1"], "type": "Antibiotic", "dosage": "100 mg twice daily", "purpose": "Respiratory infections, acne, malaria prevention", "availability": "Prescription", "price_range": "₹40-200", "side_effects": "Photosensitivity, GI upset"},
    
    # Skin Conditions
    {"name": "Hydrocortisone Cream", "brand_names": ["Cortisone"], "type": "Topical Steroid", "dosage": "Apply thin layer 2-3 times daily", "purpose": "Skin inflammation, rash, eczema, allergic reactions", "availability": "OTC", "price_range": "₹30-150", "side_effects": "Skin thinning with prolonged use"},
    {"name": "Antifungal Cream", "brand_names": ["Clotrimazole", "Candid"], "type": "Antifungal", "dosage": "Apply twice daily", "purpose": "Fungal skin infections, ringworm, athlete's foot", "availability": "OTC", "price_range": "₹40-150", "side_effects": "Local irritation"},
    {"name": "Calamine Lotion", "brand_names": ["Caladryl"], "type": "Topical", "dosage": "Apply as needed", "purpose": "Itching, minor burns, insect bites, rashes", "availability": "OTC", "price_range": "₹30-100", "side_effects": "Minimal"},
    
    # Diabetes Management
    {"name": "Metformin", "brand_names": ["Glucophage", "Glycomet"], "type": "Antidiabetic", "dosage": "500-1000 mg twice daily", "purpose": "Type 2 diabetes, blood sugar control", "availability": "Prescription", "price_range": "₹20-150", "side_effects": "GI upset, lactic acidosis (rare)"},
    {"name": "Glimepiride", "brand_names": ["Amaryl"], "type": "Antidiabetic", "dosage": "1-4 mg daily", "purpose": "Type 2 diabetes", "availability": "Prescription", "price_range": "₹30-200", "side_effects": "Hypoglycemia, weight gain"},
    
    # Hypertension
    {"name": "Amlodipine", "brand_names": ["Norvasc"], "type": "Calcium Channel Blocker", "dosage": "5-10 mg daily", "purpose": "High blood pressure, angina", "availability": "Prescription", "price_range": "₹20-150", "side_effects": "Ankle swelling, headache"},
    {"name": "Losartan", "brand_names": ["Cozaar"], "type": "ARB", "dosage": "50-100 mg daily", "purpose": "Hypertension, kidney protection in diabetes", "availability": "Prescription", "price_range": "₹50-250", "side_effects": "Dizziness, hyperkalemia"},
    
    # Pain (Specialized)
    {"name": "Tramadol", "brand_names": ["Ultracet"], "type": "Opioid Analgesic", "dosage": "50-100 mg every 4-6h", "purpose": "Moderate to severe pain", "availability": "Prescription", "price_range": "₹30-200", "side_effects": "Dizziness, nausea, dependence risk"},
    {"name": "Capsaicin Cream", "brand_names": ["Zostrix"], "type": "Topical Analgesic", "dosage": "Apply 3-4 times daily", "purpose": "Muscle pain, arthritis, nerve pain", "availability": "OTC", "price_range": "₹150-400", "side_effects": "Burning sensation initially"},
    
    # Mental Health
    {"name": "Melatonin", "brand_names": ["Melatonin"], "type": "Sleep Aid", "dosage": "3-5 mg at bedtime", "purpose": "Insomnia, sleep disorders", "availability": "OTC", "price_range": "₹200-600", "side_effects": "Drowsiness, vivid dreams"},
    
    # General Health & Immunity
    {"name": "Multivitamin", "brand_names": ["Revital", "Supradyn"], "type": "Supplement", "dosage": "1 tablet daily", "purpose": "General health and immunity support", "availability": "OTC", "price_range": "₹100-500", "side_effects": "Minimal when taken as directed"},
    {"name": "Vitamin C", "brand_names": ["Limcee", "Celin"], "type": "Supplement", "dosage": "500-1000 mg daily", "purpose": "Immunity boost, cold prevention, antioxidant", "availability": "OTC", "price_range": "₹50-200", "side_effects": "Diarrhea at high doses"},
    {"name": "Vitamin D3", "brand_names": ["Calcirol"], "type": "Supplement", "dosage": "1000-2000 IU daily", "purpose": "Bone health, immunity, deficiency treatment", "availability": "OTC", "price_range": "₹100-400", "side_effects": "Minimal"},
    {"name": "Zinc", "brand_names": ["Zincovit"], "type": "Supplement", "dosage": "15-30 mg daily", "purpose": "Immunity, wound healing, cold duration reduction", "availability": "OTC", "price_range": "₹50-300", "side_effects": "Nausea if taken on empty stomach"},
]

# ------------------------------------------------------------------------------------
# Compound to Herb Mapping (for user-friendly herbal recommendations)
# ------------------------------------------------------------------------------------
COMPOUND_TO_HERB = {
    'withaferin a': 'Ashwagandha',
    'curcumin': 'Turmeric',
    'gingerol': 'Ginger',
    'azadirachtin': 'Neem',
    'eugenol': 'Clove',
    'allicin': 'Garlic',
    'quercetin': 'Onion',
    'menthol': 'Peppermint',
    'thymol': 'Thyme',
    'ursolic acid': 'Holy Basil (Tulsi)',
    'berberine': 'Turmeric',
    'piperine': 'Black Pepper',
    'papain': 'Papaya',
    'bromelain': 'Pineapple',
    'resveratrol': 'Grapes',
    'capsaicin': 'Cayenne Pepper',
    'anthocyanin': 'Berries',
    'silymarin': 'Milk Thistle',
}

# ------------------------------------------------------------------------------------
# Drug Safety Warnings (for restricted/controversial medications)
# ------------------------------------------------------------------------------------
DRUG_SAFETY_WARNINGS = {
    'Nimesulide': '⚠️ RESTRICTED: Not recommended for children under 12. Use only under medical supervision. Risk of liver toxicity.',
    'Metamizole': '⚠️ RESTRICTED: Banned in many countries due to agranulocytosis risk. Use only if prescribed by specialist.',
    'Aspirin': '⚠️ WARNING: Not for children under 12 (Reye\'s syndrome risk). Consult doctor if on blood thinners.',
    'Ibuprofen': '⚠️ CAUTION: Not for prolonged use. Risk of GI bleeding and kidney damage. Take with food.',
    'Diclofenac': '⚠️ RESTRICTED: Cardiovascular risk. Not for heart disease patients. Prescription required in many countries.',
    'Tramadol': '⚠️ CONTROLLED: Opioid - addiction risk. Schedule H drug. Only use as prescribed. Not for children.',
    'Ciprofloxacin': '⚠️ WARNING: Risk of tendon rupture. Not for children/pregnant women. Complete full course.',
    'Doxycycline': '⚠️ WARNING: Avoid sunlight exposure. Not for children under 8 or pregnant women. Stains teeth.',
    'Metronidazole': '⚠️ WARNING: Absolutely NO ALCOHOL while taking or 48h after. Causes severe reaction.',
    'Amoxicillin': '⚠️ CAUTION: Check for penicillin allergy before use. Complete full course even if better.',
    'Azithromycin': '⚠️ CAUTION: Complete full course. Not for heart arrhythmia patients.',
}

# ------------------------------------------------------------------------------------
# Large lookup dictionaries (spelling_map, disease_mapping, condition_info, icons)
# ------------------------------------------------------------------------------------
# This block is heavily expanded to avoid missing keys and reduce errors at runtime.
# You can extend these further by editing below.
spelling_map = {
    # common typos / variants (sample of many)
    'fevr': 'fever', 'feverr': 'fever', 'feaver': 'fever', 'feber': 'fever',
    'coough': 'cough', 'couf': 'cough', 'caugh': 'cough',
    'colud': 'cold', 'coldf': 'cold',
    'asthma': 'asthma', 'astma': 'asthma', 'asthama': 'asthma',
    'bronchitiss': 'bronchitis', 'bronchit': 'bronchitis',
    'pneumona': 'pneumonia', 'pnemonia': 'pneumonia',
    'throatt': 'throat', 'throad': 'throat', 'soar throat': 'sore throat',
    'runnynose': 'runny nose', 'sneezee': 'sneeze',
    'vommit': 'vomit', 'vommiting': 'vomiting', 'nausia': 'nausea',
    'stomuch': 'stomach', 'stomache': 'stomach',
    'diarea': 'diarrhea', 'diarrhoea': 'diarrhea',
    'indegestion': 'indigestion',
    'migrane': 'migraine', 'headeache': 'headache',
    'dipression': 'depression', 'anxity': 'anxiety',
    'insomina': 'insomnia', 'fatige': 'fatigue',
    'diabities': 'diabetes', 'diabets': 'diabetes',
    'maleriya': 'malaria', 'dengee': 'dengue',
    # add more as needed...
}

# Map disease names to embedding-friendly names (lots of fallbacks)
disease_mapping = {
    "Common Cold": "A Common Cold",
    "Cold": "A Common Cold",
    "Flu": "A Common Cold",
    "Influenza": "A Common Cold",
    "Cough": "A Common Cold",
    "Sore Throat": "A Common Cold",
    "Rhinitis": "A Common Cold",
    "Asthma": "Bronchial Asthma",
    "Bronchitis": "Bronchial Asthma",
    "Pneumonia": "Pneumonia",
    "COVID-19": "Pneumonia",
    "Sinusitis": "A Common Cold",
    "Dengue": "Fever",
    "Malaria": "Fever",
    "Typhoid": "Fever",
    "Gastroenteritis": "Fever",
    "Food Poisoning": "Fever",
    "Migraine": "Fever",
    "Headache": "Fever",
    "Fever": "Fever",
    "Hypertension": "Fever",
    "Diabetes": "Fever",
    "Arthritis": "Fever",
    "Acidity": "Fever",
    "Indigestion": "Fever",
    "Constipation": "Fever",
    "UTI": "Fever",
    "Jaundice": "Fever",
    # default cases will fallback to original disease string if not found
}

# Detailed condition information (safe 2-line descriptions)
condition_info = {
    'Asthma': [
        '  Asthma is a chronic inflammatory disease of the airways causing variable airflow obstruction.',
        '  Symptoms include wheeze, breathlessness, chest tightness and cough; avoid triggers and use inhalers as prescribed.'
    ],
    'Fever': [
        '  Fever is elevated body temperature often due to infection or inflammation.',
        '  Monitor temperature, stay hydrated and seek care if very high or prolonged.'
    ],
    'Common Cold': [
        '  A mild viral infection of the upper respiratory tract.',
        '  Symptoms include runny nose, sore throat, cough and sneezing; usually self-limiting.'
    ],
    'Gastroenteritis': [
        '  Inflammation of the stomach and intestines usually causing diarrhea and vomiting.',
        '  Rehydration and rest are essential; seek help if dehydrated or severe.'
    ],
    'Headache': [
        '  Pain in the head area with many potential causes (tension, migraine, infection).',
        '  Manage with rest, hydration, analgesics; seek care if sudden severe or with neurological signs.'
    ],
    'Migraine': [
        '  Recurrent moderate-to-severe headaches often with nausea and sensitivity to light/sound.',
        '  Trigger management and targeted medications are used under guidance.'
    ],
    'Arthritis': [
        '  Arthritis is inflammation of one or more joints causing pain, stiffness, and swelling.',
        '  May be osteoarthritis (wear-and-tear) or rheumatoid (autoimmune); both need proper management.'
    ],
    'Osteoarthritis': [
        '  Degenerative joint disease caused by wear-and-tear over time, common in older adults.',
        '  Joint pain worsens with activity and improves with rest; physical therapy helps.'
    ],
    'Rheumatoid Arthritis': [
        '  Autoimmune condition causing joint inflammation, often affecting multiple joints symmetrically.',
        '  Early diagnosis and treatment with immunosuppressants can help prevent joint damage.'
    ],
    'Joint Pain': [
        '  Joint pain can result from arthritis, injury, inflammation, or muscle strain.',
        '  Determine if localized (single joint) or generalized (multiple joints) for proper diagnosis.'
    ],
    'Dengue': [
        '  Mosquito-borne viral infection causing high fever, joint pain and low platelets.',
        '  Medical follow-up is important to monitor platelet counts.'
    ],
    'Malaria': [
        '  Parasitic infection causing cyclical fevers; can be severe without treatment.',
        '  Prompt diagnosis and anti-malarial therapy are required.'
    ],
    'UTI': [
        '  Infection of urinary tract often causing painful urination and frequency.',
        '  Seek antibiotics if confirmed; hydrate and consult your clinician.'
    ],
    # Add many more 2-line descriptions as needed (kept short for brevity)
}

# Icons to avoid missing keys
severity_icons = {
    'CRITICAL': '🔴', 'HIGH': '🟠', 'SEVERE': '🟥', 'MODERATE': '🟡', 'LOW': '🟢', 'MILD': '🟢', 'UNKNOWN': '⚪'
}
availability_icons = {
    'OTC': '🟢', 'Prescription': '🔵', 'Limited': '🟡', 'Unavailable': '🔴', 'Herbal': '🌿', 'Home Remedy': '🪴'
}

# ------------------------------------------------------------------------------------
# Utility helpers
# ------------------------------------------------------------------------------------
def load_csv_or_fallback(data_dir: str = "data"):
    """
    Try to load CSVs from data_dir (expected: diseases.csv, ingredients.csv, targets.csv, herbs.csv)
    If pandas not available or files missing, return embedded sample data as dict of DataFrames/lists
    
    All file reads use UTF-8 encoding to avoid encoding issues.
    """
    knowledge = {}
    if pd is None:
        # pandas not available; return sample data
        knowledge["diseases"] = SAMPLE_DISEASES
        knowledge["ingredients"] = SAMPLE_INGREDIENTS
        knowledge["targets"] = SAMPLE_TARGETS
        knowledge["herbs"] = SAMPLE_HERBS
        return knowledge

    try:
        # try reading CSVs, use fallbacks if files missing
        def try_read(fname, fallback):
            path = os.path.join(data_dir, fname)
            if os.path.exists(path):
                try:
                    return pd.read_csv(path, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        return pd.read_csv(path, encoding='latin-1')
                    except Exception:
                        return pd.DataFrame(fallback)
                except Exception:
                    return pd.DataFrame(fallback)
            else:
                return pd.DataFrame(fallback)

        knowledge["diseases"] = try_read("diseases.csv", SAMPLE_DISEASES)
        knowledge["ingredients"] = try_read("ingredients.csv", SAMPLE_INGREDIENTS)
        knowledge["targets"] = try_read("targets.csv", SAMPLE_TARGETS)
        knowledge["herbs"] = try_read("herbs.csv", SAMPLE_HERBS)
    except Exception as e:
        # if anything fails, use sample data
        knowledge["diseases"] = pd.DataFrame(SAMPLE_DISEASES)
        knowledge["ingredients"] = pd.DataFrame(SAMPLE_INGREDIENTS)
        knowledge["targets"] = pd.DataFrame(SAMPLE_TARGETS)
        knowledge["herbs"] = pd.DataFrame(SAMPLE_HERBS)
    return knowledge

# ------------------------------------------------------------------------------------
# Keep original function names but wire to fallbacks above
# ------------------------------------------------------------------------------------
def load_knowledge_base(data_dir="data") -> Dict:
    """
    Load all medical knowledge data from CSVs or fallback data.
    Robust to missing files, encoding issues, and pandas unavailability.
    Always returns a valid knowledge dictionary.
    """
    try:
        raw = load_csv_or_fallback(data_dir)
        knowledge = {}

        # If pandas DataFrames, keep them; else they are lists/dicts
        knowledge["diseases"] = raw.get("diseases", SAMPLE_DISEASES)
        knowledge["ingredients"] = raw.get("ingredients", SAMPLE_INGREDIENTS)
        knowledge["targets"] = raw.get("targets", SAMPLE_TARGETS)
        knowledge["herbs"] = raw.get("herbs", SAMPLE_HERBS)

        # Create lookup tables (works for both DataFrame and list-of-dicts)
        try:
            # when pandas DataFrame
            tgt_df = knowledge["targets"]
            if hasattr(tgt_df, "iterrows"):
                knowledge["target_to_disease"] = dict(
                    zip(tgt_df["target"].astype(str).str.strip(), tgt_df["disease"].astype(str).str.strip())
                )
            else:
                # list of dicts
                mapping = {}
                for row in tgt_df:
                    mapping[str(row.get("target", "")).strip()] = str(row.get("disease", "")).strip()
                knowledge["target_to_disease"] = mapping
        except Exception:
            knowledge["target_to_disease"] = {}

        # Build ingredient_to_targets
        try:
            ing_df = knowledge["ingredients"]
            mapping = {}
            if hasattr(ing_df, "iterrows"):
                for _, row in ing_df.iterrows():
                    ing = str(row.get("ingredient", "")).strip()
                    tgt = str(row.get("target", "")).strip()
                    mapping.setdefault(ing, []).append(tgt)
            else:
                for row in ing_df:
                    ing = str(row.get("ingredient", "")).strip()
                    tgt = str(row.get("target", "")).strip()
                    mapping.setdefault(ing, []).append(tgt)
            knowledge["ingredient_to_targets"] = mapping
        except Exception:
            knowledge["ingredient_to_targets"] = {}

        return knowledge
    except Exception as e:
        # Last-resort fallback: return minimal but valid knowledge base
        return {
            "diseases": SAMPLE_DISEASES,
            "ingredients": SAMPLE_INGREDIENTS,
            "targets": SAMPLE_TARGETS,
            "herbs": SAMPLE_HERBS,
            "target_to_disease": {},
            "ingredient_to_targets": {}
        }

def get_herb_info(herb_name: str, herbs_df) -> Dict:
    """Get detailed information about an herb. herbs_df can be DataFrame or list."""
    try:
        if pd is not None and hasattr(herbs_df, "iloc"):
            row = herbs_df[herbs_df['herb'].str.lower() == herb_name.lower()]
            if row.empty:
                return {}
            row = row.iloc[0]
            return {
                "name": row.get("herb", herb_name),
                "benefits": row.get("benefits", ""),
                "active_compounds": row.get("active_compounds", ""),
                "usage": row.get("usage", ""),
            }
        else:
            # list of dicts fallback
            for r in herbs_df:
                if str(r.get("herb", "")).lower() == herb_name.lower():
                    return {
                        "name": r.get("herb", herb_name),
                        "benefits": r.get("benefits", ""),
                        "active_compounds": r.get("active_compounds", ""),
                        "usage": r.get("usage", ""),
                    }
    except Exception:
        pass
    return {}

def suggest_drugs_for_disease(disease: str, top_n: int = 5) -> List[Dict]:
    """
    Suggest pharmaceutical drugs/tablets available in medical stores for a disease.
    If DrugDatabase is not available, use embedded sample list and basic matching.
    """
    if HAS_DRUG_DB:
        try:
            db = DrugDatabase()
            drugs = db.get_drugs_sorted_by_commonality(disease)
            formatted = []
            for drug in drugs[:top_n]:
                formatted.append({
                    "name": drug.get("name"),
                    "brand_names": drug.get("brand_names", []),
                    "type": drug.get("type"),
                    "dosage": drug.get("dosage"),
                    "purpose": drug.get("purpose"),
                    "availability": drug.get("availability"),
                    "price_range": drug.get("price_range"),
                    "side_effects": drug.get("side_effects")
                })
            return formatted
        except Exception:
            # fallback to sample
            pass

    # Fallback simple matching from SAMPLE_DRUGS
    matched = []
    disease_l = (disease or "").lower()
    
    # Comprehensive disease -> drug mapping heuristics with expanded keywords
    for d in SAMPLE_DRUGS:
        name = d.get("name", "")
        purpose = d.get("purpose", "").lower()
        dtype = d.get("type", "").lower()
        
        # Throat conditions (tonsillitis, pharyngitis, sore throat)
        if any(k in disease_l for k in ["throat", "tonsil", "pharyn", "laryn", "strep"]):
            if any(k in purpose for k in ["throat", "infection", "pain", "soothe"]) or \
               "antibiotic" in dtype or "lozenge" in dtype or "analgesic" in dtype or "antiseptic" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Respiratory (cold, cough, flu, bronchitis, asthma)
        if any(k in disease_l for k in ["cough", "cold", "flu", "respiratory", "bronch", "pneumo", "asthma", "wheez", "sinus", "congestion"]):
            if any(k in purpose for k in ["cough", "cold", "respiratory", "mucus", "allergy", "congestion", "breathing", "asthma", "bronch"]) or \
               "antihistamine" in dtype or "cough" in dtype or "expectorant" in dtype or "decongestant" in dtype or "bronchodilator" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Fever and general pain
        if any(k in disease_l for k in ["fever", "headache", "pain", "muscle", "strain", "back", "sprain", "migraine", "general", "ache", "body", "joint"]):
            if any(k in purpose for k in ["fever", "pain", "inflammation", "ache"]) or \
               "analgesic" in dtype or "nsaid" in dtype or "antipyretic" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Digestive issues (comprehensive)
        if any(k in disease_l for k in ["stomach", "gastric", "gastro", "ulcer", "acidity", "indigestion", "reflux", "gerd", "heartburn", "ibs", "crohn", "colitis"]):
            if any(k in purpose for k in ["acid", "gastric", "reflux", "stomach", "heartburn", "digestive", "ibs", "cramps", "spasms"]) or \
               "pump inhibitor" in dtype or "h2 blocker" in dtype or "antacid" in dtype or "antispasmodic" in dtype or "probiotic" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Diarrhea, vomiting
        if any(k in disease_l for k in ["diarr", "loose", "motion", "vomit", "nausea"]):
            if any(k in purpose for k in ["diarr", "rehydr", "vomit", "nausea", "gut", "flora"]) or \
               "anti-diarrheal" in dtype or "anti-emetic" in dtype or "rehydration" in purpose or "probiotic" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Allergy & Skin
        if any(k in disease_l for k in ["allerg", "rash", "itch", "hive", "eczema", "dermat", "skin"]):
            if any(k in purpose for k in ["allergy", "itch", "rash", "skin", "inflammation"]) or \
               "antihistamine" in dtype or "steroid" in dtype or "antifungal" in dtype or "topical" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Infections (bacterial, fungal)
        if any(k in disease_l for k in ["infection", "bacterial", "uti", "kidney", "fungal", "ringworm", "athlete"]):
            if any(k in purpose for k in ["infection", "bacterial", "uti", "kidney", "fungal"]) or \
               "antibiotic" in dtype or "antifungal" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Diabetes
        if any(k in disease_l for k in ["diabet", "sugar", "glucose"]):
            if any(k in purpose for k in ["diabetes", "blood sugar", "glucose"]) or \
               "antidiabetic" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Hypertension
        if any(k in disease_l for k in ["hypertens", "blood pressure", "bp", "high pressure"]):
            if any(k in purpose for k in ["blood pressure", "hypertension", "bp"]) or \
               "calcium channel blocker" in dtype or "arb" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # Sleep & Mental Health
        if any(k in disease_l for k in ["insomnia", "sleep", "anxiety", "stress", "depression"]):
            if any(k in purpose for k in ["sleep", "insomnia"]) or \
               "sleep aid" in dtype:
                if d not in matched:
                    matched.append(d)
        
        # General health & immunity
        if any(k in disease_l for k in ["immun", "weak", "fatigue", "tired", "vitamin", "deficiency"]):
            if any(k in purpose for k in ["immunity", "health", "vitamin", "bone", "antioxidant"]) or \
               "supplement" in dtype:
                if d not in matched:
                    matched.append(d)
        
        if len(matched) >= top_n:
            break
    
    # If still no matches, provide general remedies (improved fallback)
    if not matched:
        # For unknown/general conditions, offer comprehensive general support
        for d in SAMPLE_DRUGS:
            purpose = d.get("purpose", "").lower()
            dtype = d.get("type", "").lower()
            # Include pain relievers, immunity support, and common OTC drugs
            if any(k in purpose for k in ["pain", "fever", "immunity", "health"]) or \
               "analgesic" in dtype or "nsaid" in dtype or "supplement" in dtype:
                matched.append(d)
            if len(matched) >= top_n:
                break
    
    return matched[:top_n]

def load_drug_interactions(data_dir: str = "data") -> Dict:
    """Load drug interaction database from CSV if available; fallback empty dict."""
    interactions = {}
    if pd is None:
        return interactions
    path = os.path.join(data_dir, "drug_interactions.csv")
    if not os.path.exists(path):
        return interactions
    try:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            drug1 = str(row.get('drug1', '')).lower().strip()
            drug2 = str(row.get('drug2', '')).lower().strip()
            key = tuple(sorted([drug1, drug2]))
            interactions[key] = {
                'severity': row.get('severity', 'MODERATE'),
                'effect': row.get('effect', ''),
                'recommendation': row.get('recommendation', '')
            }
    except Exception:
        pass
    return interactions

def check_drug_interactions(drug_list: List[str], interactions: Dict = None) -> List[Dict]:
    """Check drug interactions using preloaded interactions dict."""
    if interactions is None:
        interactions = load_drug_interactions()
    if not interactions or len(drug_list) < 2:
        return []
    detected = []
    for i in range(len(drug_list)):
        for j in range(i+1, len(drug_list)):
            a = (drug_list[i] or "").lower().strip()
            b = (drug_list[j] or "").lower().strip()
            key = tuple(sorted([a, b]))
            if key in interactions:
                data = interactions[key]
                detected.append({
                    'drug1': drug_list[i],
                    'drug2': drug_list[j],
                    'severity': data.get('severity', 'MODERATE'),
                    'effect': data.get('effect', ''),
                    'recommendation': data.get('recommendation', '')
                })
    return detected

def load_allergies_db(data_dir: str = "data") -> Dict:
    """Load allergies database if available; fallback empty dict."""
    allergies = {}
    if pd is None:
        return allergies
    path = os.path.join(data_dir, "allergies.csv")
    if not os.path.exists(path):
        return allergies
    try:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            allergen = str(row.get('allergen', '')).lower().strip()
            allergies[allergen] = {
                'category': row.get('category', ''),
                'severity': row.get('severity', 'MODERATE'),
                'cross_reactions': str(row.get('cross_reactions', '')).split(';') if pd.notna(row.get('cross_reactions', '')) else [],
                'symptoms': str(row.get('symptoms', '')).split(';') if pd.notna(row.get('symptoms', '')) else [],
                'common_sources': row.get('common_sources', '')
            }
    except Exception:
        pass
    return allergies

def check_allergies(drugs: List[Dict], user_allergies: Set[str] = None, allergies_db: Dict = None) -> List[Dict]:
    """Check if recommended drugs contain allergens (basic name-based check)."""
    if not user_allergies or not drugs:
        return []
    if allergies_db is None:
        allergies_db = load_allergies_db()
    warnings = []
    for drug in drugs:
        drug_name = (drug.get('name') or "").lower()
        for allergen in user_allergies:
            a = allergen.lower().strip()
            if a in drug_name or drug_name in a:
                warnings.append({
                    'drug': drug.get('name'),
                    'allergen': allergen,
                    'severity': allergies_db.get(a, {}).get('severity', 'MODERATE'),
                    'warning': f"⚠️ ALLERGY ALERT: {drug.get('name')} may contain {allergen}"
                })
    return warnings

# ------------------------------------------------------------------------------------
# Suggest herbal ingredients for a disease
# This uses embeddings if available, otherwise returns simple heuristic list
# ------------------------------------------------------------------------------------
def suggest_ingredients_for_disease(
    disease: str,
    embeddings_path: str = "data/embeddings.kv",
    model_path: str = "data/stack_model.pkl",
    knowledge: Dict = None
) -> List[Tuple[str, float]]:
    """
    Suggest herbal ingredients for a detected disease.
    If embeddings/model exist and gensim/joblib available, uses them.
    Otherwise returns heuristic list based on knowledge and fallback mapping.
    """
    # If gensim/joblib not available or files missing, fallback
    if KeyedVectors is None or joblib is None or np is None:
        # Enhanced heuristic mapping with comprehensive coverage
        d = (disease or "").lower()
        heuristics = []
        
        # Digestive & Gastrointestinal
        if any(k in d for k in ["gastro", "diarr", "stomach", "digest", "ibs", "crohn", "colitis", "acid", "reflux", "gerd", "nausea", "vomit"]):
            heuristics = [("Ginger", 0.90), ("Peppermint", 0.85), ("Turmeric", 0.80), ("Chamomile", 0.75), ("Fennel", 0.70)]
        
        # Respiratory & Throat
        elif any(k in d for k in ["cold", "cough", "bronch", "asthma", "throat", "tonsil", "pharyn", "laryn", "respiratory", "pneumo", "sinus"]):
            heuristics = [("Tulsi (Holy Basil)", 0.90), ("Ginger", 0.85), ("Licorice", 0.80), ("Eucalyptus", 0.75), ("Honey", 0.70)]
        
        # Fever & Infections
        elif any(k in d for k in ["fever", "dengue", "malaria", "viral", "infection", "flu", "influenza"]):
            heuristics = [("Tulsi (Holy Basil)", 0.88), ("Giloy", 0.85), ("Neem", 0.80), ("Turmeric", 0.75), ("Black Pepper", 0.70)]
        
        # Pain & Inflammation
        elif any(k in d for k in ["headache", "migraine", "pain", "muscle", "strain", "back", "sprain", "arthritis", "rheumat", "inflamm"]):
            heuristics = [("Turmeric", 0.90), ("Ginger", 0.85), ("Boswellia", 0.82), ("Willow Bark", 0.78), ("Devil's Claw", 0.75)]
        
        # Kidney & Urinary
        elif any(k in d for k in ["kidney", "stone", "renal", "urinary", "uti", "bladder", "uric"]):
            heuristics = [("Punarnava", 0.88), ("Gokshura", 0.85), ("Cranberry", 0.80), ("Dandelion", 0.75), ("Parsley", 0.70)]
        
        # Liver & Detox
        elif any(k in d for k in ["liver", "hepat", "jaundice", "detox", "toxin"]):
            heuristics = [("Milk Thistle", 0.90), ("Dandelion Root", 0.85), ("Turmeric", 0.82), ("Bhuiamlaki", 0.80), ("Artichoke", 0.75)]
        
        # Diabetes & Blood Sugar
        elif any(k in d for k in ["diabet", "sugar", "glucose", "insulin"]):
            heuristics = [("Bitter Melon (Karela)", 0.88), ("Fenugreek", 0.85), ("Cinnamon", 0.82), ("Gymnema", 0.80), ("Jamun", 0.75)]
        
        # Hypertension & Cardiovascular
        elif any(k in d for k in ["hypertens", "blood pressure", "bp", "cardiov", "heart", "cholesterol"]):
            heuristics = [("Garlic", 0.88), ("Hawthorn", 0.85), ("Arjuna", 0.82), ("Hibiscus", 0.78), ("Flaxseed", 0.75)]
        
        # Skin Conditions
        elif any(k in d for k in ["skin", "rash", "eczema", "psoria", "acne", "dermat", "itch"]):
            heuristics = [("Neem", 0.90), ("Aloe Vera", 0.88), ("Turmeric", 0.85), ("Tea Tree Oil", 0.80), ("Manjistha", 0.75)]
        
        # Anxiety & Stress
        elif any(k in d for k in ["anxiety", "stress", "tension", "nervous", "panic", "worry"]):
            heuristics = [("Ashwagandha", 0.90), ("Brahmi", 0.85), ("Chamomile", 0.82), ("Lavender", 0.78), ("Valerian Root", 0.75)]
        
        # Insomnia & Sleep
        elif any(k in d for k in ["insomnia", "sleep", "sleepless"]):
            heuristics = [("Valerian Root", 0.88), ("Ashwagandha", 0.85), ("Chamomile", 0.82), ("Passionflower", 0.78), ("Lavender", 0.75)]
        
        # Immunity & General Health
        elif any(k in d for k in ["immun", "weak", "fatigue", "general", "wellness", "health", "tired"]):
            heuristics = [("Ashwagandha", 0.88), ("Giloy", 0.85), ("Tulsi", 0.82), ("Amla", 0.80), ("Ginseng", 0.75)]
        
        # Allergy
        elif any(k in d for k in ["allerg", "hives", "rhinitis", "hay fever"]):
            heuristics = [("Butterbur", 0.85), ("Stinging Nettle", 0.82), ("Quercetin", 0.80), ("Turmeric", 0.75), ("Ginger", 0.70)]
        
        # Women's Health
        elif any(k in d for k in ["menstrual", "period", "pms", "menstru", "cramp"]):
            heuristics = [("Shatavari", 0.88), ("Ginger", 0.85), ("Chamomile", 0.80), ("Cinnamon", 0.75), ("Fennel", 0.70)]
        
        # Anemia & Blood Health
        elif any(k in d for k in ["anemia", "anaemia", "iron", "blood"]):
            heuristics = [("Punarnava", 0.85), ("Beetroot", 0.82), ("Spirulina", 0.80), ("Nettle", 0.75), ("Moringa", 0.70)]
        
        # Weight Management
        elif any(k in d for k in ["weight", "obesity", "fat", "overweight"]):
            heuristics = [("Green Tea", 0.85), ("Garcinia Cambogia", 0.80), ("Triphala", 0.78), ("Guggul", 0.75), ("Cinnamon", 0.70)]
        
        # Default/Generic conditions
        else:
            heuristics = [("Turmeric", 0.70), ("Ginger", 0.68), ("Tulsi", 0.65), ("Neem", 0.60), ("Ashwagandha", 0.58)]
        
        return heuristics[:5]

    # If embeddings present, try to use them (kept backward-compatible)
    try:
        if not os.path.exists(embeddings_path) or not os.path.exists(model_path):
            # Files don't exist, use enhanced heuristic fallback
            d = (disease or "").lower()
            heuristics = []
            
            # Same comprehensive mapping as above
            if any(k in d for k in ["gastro", "diarr", "stomach", "digest", "ibs", "acid", "reflux", "gerd"]):
                heuristics = [("Ginger", 0.90), ("Peppermint", 0.85), ("Turmeric", 0.80), ("Chamomile", 0.75), ("Fennel", 0.70)]
            elif any(k in d for k in ["cold", "cough", "bronch", "asthma", "throat", "tonsil", "respiratory"]):
                heuristics = [("Tulsi (Holy Basil)", 0.90), ("Ginger", 0.85), ("Licorice", 0.80), ("Eucalyptus", 0.75), ("Honey", 0.70)]
            elif any(k in d for k in ["fever", "dengue", "malaria", "viral", "infection"]):
                heuristics = [("Tulsi (Holy Basil)", 0.88), ("Giloy", 0.85), ("Neem", 0.80), ("Turmeric", 0.75), ("Black Pepper", 0.70)]
            elif any(k in d for k in ["headache", "migraine", "pain", "muscle", "strain", "arthritis", "inflamm"]):
                heuristics = [("Turmeric", 0.90), ("Ginger", 0.85), ("Boswellia", 0.82), ("Willow Bark", 0.78), ("Devil's Claw", 0.75)]
            elif any(k in d for k in ["kidney", "stone", "renal", "urinary", "uti"]):
                heuristics = [("Punarnava", 0.88), ("Gokshura", 0.85), ("Cranberry", 0.80), ("Dandelion", 0.75), ("Parsley", 0.70)]
            elif any(k in d for k in ["diabet", "sugar", "glucose"]):
                heuristics = [("Bitter Melon (Karela)", 0.88), ("Fenugreek", 0.85), ("Cinnamon", 0.82), ("Gymnema", 0.80), ("Jamun", 0.75)]
            elif any(k in d for k in ["hypertens", "blood pressure", "bp", "cardiov"]):
                heuristics = [("Garlic", 0.88), ("Hawthorn", 0.85), ("Arjuna", 0.82), ("Hibiscus", 0.78), ("Flaxseed", 0.75)]
            elif any(k in d for k in ["skin", "rash", "eczema", "acne", "itch"]):
                heuristics = [("Neem", 0.90), ("Aloe Vera", 0.88), ("Turmeric", 0.85), ("Tea Tree Oil", 0.80), ("Manjistha", 0.75)]
            elif any(k in d for k in ["anxiety", "stress", "nervous"]):
                heuristics = [("Ashwagandha", 0.90), ("Brahmi", 0.85), ("Chamomile", 0.82), ("Lavender", 0.78), ("Valerian Root", 0.75)]
            elif any(k in d for k in ["immun", "weak", "general", "health"]):
                heuristics = [("Ashwagandha", 0.88), ("Giloy", 0.85), ("Tulsi", 0.82), ("Amla", 0.80), ("Ginseng", 0.75)]
            else:
                heuristics = [("Turmeric", 0.70), ("Ginger", 0.68), ("Tulsi", 0.65), ("Neem", 0.60), ("Ashwagandha", 0.58)]
            return heuristics[:5]
        emb = KeyedVectors.load(embeddings_path)
        model = joblib.load(model_path)
        ingredients = [l.strip() for l in open("data/nodes_ingredients.txt").read().splitlines() if l.strip()]
        lookup_name = disease_mapping.get(disease, disease)
        if lookup_name not in emb.key_to_index:
            # Disease not in embeddings, use heuristic fallback
            d = (disease or "").lower()
            heuristics = []
            if "gastro" in d or "diarr" in d or "stomach" in d:
                heuristics = [("Ginger", 0.85), ("Peppermint", 0.75), ("Turmeric", 0.6), ("ORS", 0.5)]
            elif "fever" in d or "dengue" in d or "malaria" in d:
                heuristics = [("Withaferin A", 0.7), ("Papaya leaf extract", 0.6), ("Turmeric", 0.5)]
            elif "cold" in d or "cough" in d or "bronch" in d or "asthma" in d:
                heuristics = [("Tulsi", 0.8), ("Ginger", 0.7), ("Licorice", 0.6)]
            elif "headache" in d or "migraine" in d:
                heuristics = [("Peppermint", 0.7), ("Feverfew", 0.6), ("Turmeric", 0.5)]
            elif "muscle" in d or "strain" in d or "back pain" in d or "sprain" in d or "pain" in d:
                heuristics = [("Turmeric", 0.8), ("Ginger", 0.75), ("Arnica", 0.7), ("Boswellia", 0.65)]
            elif "kidney" in d or "stone" in d or "renal" in d or "urinary" in d:
                heuristics = [("Chanca Piedra", 0.8), ("Dandelion", 0.7), ("Cranberry", 0.65), ("Hydrangea", 0.6)]
            else:
                heuristics = [("Turmeric", 0.6), ("Ginger", 0.55), ("Neem", 0.45)]
            return heuristics[:5]
        scores = []
        for ing in ingredients:
            if ing in emb.key_to_index:
                feat = np.multiply(emb[ing], emb[lookup_name])
                proba = model.predict_proba([feat])[0, 1]
                scores.append((ing, float(proba)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:5]
    except Exception:
        # Exception occurred, use heuristic fallback
        d = (disease or "").lower()
        heuristics = []
        if "gastro" in d or "diarr" in d or "stomach" in d:
            heuristics = [("Ginger", 0.85), ("Peppermint", 0.75), ("Turmeric", 0.6), ("ORS", 0.5)]
        elif "fever" in d or "dengue" in d or "malaria" in d:
            heuristics = [("Withaferin A", 0.7), ("Papaya leaf extract", 0.6), ("Turmeric", 0.5)]
        elif "cold" in d or "cough" in d or "bronch" in d or "asthma" in d:
            heuristics = [("Tulsi", 0.8), ("Ginger", 0.7), ("Licorice", 0.6)]
        elif "headache" in d or "migraine" in d:
            heuristics = [("Peppermint", 0.7), ("Feverfew", 0.6), ("Turmeric", 0.5)]
        elif "muscle" in d or "strain" in d or "back pain" in d or "sprain" in d or "pain" in d:
            heuristics = [("Turmeric", 0.8), ("Ginger", 0.75), ("Arnica", 0.7), ("Boswellia", 0.65)]
        elif "kidney" in d or "stone" in d or "renal" in d or "urinary" in d:
            heuristics = [("Chanca Piedra", 0.8), ("Dandelion", 0.7), ("Cranberry", 0.65), ("Hydrangea", 0.6)]
        else:
            heuristics = [("Turmeric", 0.6), ("Ginger", 0.55), ("Neem", 0.45)]
        return heuristics[:5]

# ------------------------------------------------------------------------------------
# AI insights: uses Azure/GitHub LLM if available, otherwise uses heuristic fallback
# ------------------------------------------------------------------------------------
def generate_ai_insights(
    user_input: str,
    disease: str,
    herbal_recommendations: List[Tuple[str, float]],
    drug_recommendations: List[Dict],
    knowledge: Dict
) -> str:
    """
    Generate AI insights using multiple LLM providers with retry logic.
    
    Providers attempted (in order):
    1. OpenAI API (if OPENAI_API_KEY set)
    2. GitHub Models API (if GITHUB_TOKEN set) - with 2 retries
    3. Azure OpenAI (if AZURE_ENDPOINT and AZURE_KEY set)
    4. Local heuristic fallback
    
    Each provider has a 15-second timeout. Graceful fallback on any failure.
    """
    
    # CRITICAL FIX: Force disease-specific insights for major conditions
    # Do NOT trust LLM to follow disease-specific guidelines - use pre-verified safe text
    disease_lower = (disease or "").lower()
    herbs_list = ", ".join([h for h, _ in herbal_recommendations[:4]]) if herbal_recommendations else "herbal options"
    drugs_list = ", ".join([d.get("name") for d in drug_recommendations[:4]]) if drug_recommendations else "appropriate medications"
    
    # DENGUE / HEMORRHAGIC FEVER
    if 'dengue' in disease_lower or 'hemorrhagic' in disease_lower:
        return (
            f"Based on the reported symptoms, suspected {disease} requires immediate medical attention and proper diagnosis. "
            f"\n\n💊 MEDICATION SAFETY FOR DENGUE: For fever and pain relief, Paracetamol (Acetaminophen) is the ONLY safe option. "
            f"NSAIDs such as Aspirin, Ibuprofen, and Diclofenac must be strictly avoided due to increased bleeding risk and potential for hemorrhagic complications. "
            f"These anti-inflammatory drugs can interfere with platelet function, which is already compromised in Dengue fever. "
            f"\n\n🌿 Herbal remedies like {herbs_list} may provide supportive care through immune-boosting and anti-inflammatory properties. "
            f"Traditional herbs such as Papaya leaf extract and Giloy are commonly used in dengue management, though scientific evidence varies. "
            f"These should complement, not replace, medical treatment. "
            f"\n\n🏥 CRITICAL: Dengue requires medical supervision. Adequate hydration (oral rehydration solutions), rest, and monitoring for warning signs "
            f"(severe abdominal pain, persistent vomiting, bleeding gums, blood in stool/vomit, difficulty breathing, restlessness) are essential. "
            f"Seek immediate emergency care if any warning signs develop. Regular monitoring of platelet count and hematocrit is necessary."
        )
    
    # COVID-19
    if 'covid' in disease_lower or 'coronavirus' in disease_lower or 'sars-cov-2' in disease_lower:
        return (
            f"Based on the reported symptoms, suspected {disease} requires proper testing, isolation, and monitoring. "
            f"\n\n💊 MEDICATION FOR COVID-19: Treatment is primarily supportive. Paracetamol (Acetaminophen) is recommended for fever and body aches. "
            f"NSAIDs like Ibuprofen may be used cautiously if advised by a healthcare provider, but Paracetamol is preferred as first-line treatment. "
            f"Aspirin is not routinely recommended for COVID-19 symptom management. Antibiotics are NOT effective against viral infections and should only be used if bacterial complications develop. "
            f"\n\n🌿 Herbal support: {herbs_list} may provide immune support and symptom relief. Turmeric, ginger, and tulsi (holy basil) are traditionally used for their anti-inflammatory and immune-modulating properties. "
            f"However, these should complement medical care, not replace it. Stay well-hydrated and ensure adequate rest. "
            f"\n\n🏥 IMPORTANT: Isolate immediately, get tested, monitor oxygen levels if possible. Seek urgent medical care if you experience difficulty breathing, persistent chest pain/pressure, "
            f"confusion, inability to stay awake, or bluish lips/face. Most cases are mild, but monitoring is essential. Follow local health authority guidelines for isolation and care."
        )
    
    # MALARIA
    if 'malaria' in disease_lower:
        return (
            f"Based on the reported symptoms, suspected {disease} requires immediate medical attention and diagnostic testing (blood smear or rapid diagnostic test). "
            f"\n\n💊 MEDICATION FOR MALARIA: Malaria is a life-threatening parasitic infection that requires prescription antimalarial drugs. Paracetamol may be used for fever management under medical supervision. "
            f"Self-medication is dangerous. Treatment depends on the Plasmodium species, severity, and local drug resistance patterns. Common antimalarials include Artemisinin-based combination therapies (ACTs), Chloroquine (for sensitive strains), or Quinine. "
            f"\n\n🌿 Herbal remedies like {herbs_list} may provide supportive symptom relief but CANNOT treat the underlying parasitic infection. "
            f"Traditional herbs should never replace proven antimalarial medication. Neem and cinchona bark have historical use, but modern antimalarials are essential for cure. "
            f"\n\n🏥 CRITICAL: Malaria can progress rapidly to severe complications (cerebral malaria, organ failure). Seek immediate medical care for diagnosis and treatment. "
            f"Untreated malaria can be fatal. Prevention includes mosquito bite prevention (bed nets, repellents) and prophylactic medication in endemic areas."
        )
    
    # DIABETES
    if 'diabetes' in disease_lower or 'hyperglycemia' in disease_lower:
        return (
            f"Based on the reported symptoms, suspected {disease} requires medical evaluation, blood glucose testing, and potentially long-term management. "
            f"\n\n💊 MEDICATION FOR DIABETES: Management depends on type and severity. Type 1 requires insulin therapy. Type 2 may be managed with lifestyle changes and/or medications like Metformin, Sulfonylureas, or GLP-1 agonists. "
            f"Blood sugar control is critical to prevent complications (neuropathy, retinopathy, cardiovascular disease). Regular monitoring and medical follow-up are essential. "
            f"\n\n🌿 Herbal support: {herbs_list} may help with blood sugar regulation. Fenugreek, cinnamon, and bitter gourd have shown modest effects in studies. "
            f"However, these should complement, not replace, prescribed medications. Dietary changes (low glycemic index foods, portion control) and regular exercise are equally important. "
            f"\n\n🏥 IMPORTANT: Diabetes is a chronic condition requiring lifelong management. Work with healthcare providers to create a personalized plan. "
            f"Monitor for complications and emergency signs (very high/low blood sugar, diabetic ketoacidosis). Regular HbA1c testing and specialist consultations are recommended."
        )
    
    # HYPERTENSION
    if 'hypertension' in disease_lower or 'high blood pressure' in disease_lower:
        return (
            f"Based on the reported symptoms, suspected {disease} requires medical evaluation and blood pressure monitoring. "
            f"\n\n💊 MEDICATION FOR HYPERTENSION: Blood pressure control typically requires prescription medications (ACE inhibitors, ARBs, calcium channel blockers, diuretics, or beta-blockers). "
            f"Choice depends on blood pressure levels, age, and comorbidities. Lifestyle modifications (diet, exercise, stress management) are critical first steps and adjuncts to medication. "
            f"\n\n🌿 Herbal support: {herbs_list} may provide complementary benefits. Garlic, hibiscus tea, and certain adaptogens have shown modest blood pressure-lowering effects. "
            f"However, these should not replace prescribed antihypertensive medications. Dietary approaches (DASH diet, low sodium) and regular physical activity are proven effective. "
            f"\n\n🏥 IMPORTANT: Untreated hypertension increases risk of stroke, heart attack, and kidney disease. Regular monitoring and medical follow-up are essential. "
            f"Seek emergency care for hypertensive crisis (BP >180/120 with symptoms like severe headache, chest pain, vision changes, or difficulty breathing)."
        )
    
    # ASTHMA
    if 'asthma' in disease_lower:
        return (
            f"Based on the reported symptoms, suspected {disease} requires proper diagnosis (spirometry, peak flow monitoring) and individualized management plan. "
            f"\n\n💊 MEDICATION FOR ASTHMA: Treatment includes quick-relief inhalers (bronchodilators like Albuterol) for acute symptoms and long-term controller medications (inhaled corticosteroids, long-acting beta-agonists) for daily management. "
            f"Severity determines treatment approach. Identifying and avoiding triggers (allergens, smoke, cold air, exercise) is crucial. An asthma action plan helps manage exacerbations. "
            f"\n\n🌿 Herbal support: {herbs_list} may provide anti-inflammatory effects. Turmeric, ginger, and certain adaptogenic herbs have been studied for respiratory support. "
            f"However, these cannot replace rescue or controller inhalers. Breathing exercises and proper inhaler technique are essential components of management. "
            f"\n\n🏥 IMPORTANT: Asthma exacerbations can be life-threatening. Seek emergency care for severe shortness of breath, inability to speak in full sentences, chest tightness not relieved by rescue inhaler, "
            f"or bluish lips/nails. Always carry rescue inhaler and follow your asthma action plan."
        )
    
    herb_names = [ing for ing, _ in herbal_recommendations]
    herbs_str = ", ".join(herb_names) if herb_names else "traditional remedies"
    drug_names = [drug.get("name") for drug in drug_recommendations]
    drugs_str = ", ".join(drug_names) if drug_names else "suitable medications"
    
    system_prompt = """You are an experienced AI health assistant specializing in holistic wellness and medical science. 
Provide evidence-based, professional insights about herbal remedies and medications. 
Always emphasize consulting healthcare professionals for diagnosis and treatment. 
Be concise, clear, medically accurate, and educational."""
    
    # Disease-specific guidance for AI (dengue/hemorrhagic conditions) - NOW UNUSED FOR DENGUE
    dengue_warning = ""
    if 'dengue' in disease_lower or 'hemorrhagic' in disease_lower:
        dengue_warning = "\n\nIMPORTANT: For suspected dengue or hemorrhagic fever, NSAIDs (Aspirin, Ibuprofen, Diclofenac) are contraindicated due to bleeding risk. Only Paracetamol should be recommended under medical supervision."
    
    user_prompt = f"""Patient symptoms: {user_input}
Detected condition: {disease}
Recommended herbs: {herbs_str}
Recommended medications: {drugs_str}{dengue_warning}

Provide a professional health assessment covering:
1. How these remedies may help address the condition
2. Benefits and drawbacks of herbal vs pharmaceutical approaches
3. Important safety considerations and potential side effects
4. When to seek immediate medical attention

Format: 3-4 short paragraphs, 180-220 words total."""
    
    # Try OpenAI API (Option 1 - Preferred)
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            import urllib.request
            import json as json_module
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 500
            }
            
            req = urllib.request.Request(
                url,
                data=json_module.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json_module.loads(response.read().decode('utf-8'))
                if result.get("choices") and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    return ai_response
        except Exception as e:
            pass  # Silently try next provider
    
    # Try GitHub Models API (Option 2) with retry logic
    github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
    if github_token:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                import urllib.request
                import json as json_module
                import ssl
                
                url = "https://models.inference.ai.azure.com/chat/completions"
                headers = {
                    "Authorization": f"Bearer {github_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_tokens": 500
                }
                
                req = urllib.request.Request(
                    url,
                    data=json_module.dumps(payload).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                
                # Handle SSL certificate issues
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
                    result = json_module.loads(response.read().decode('utf-8'))
                    if result.get("choices") and len(result["choices"]) > 0:
                        ai_response = result["choices"][0]["message"]["content"]
                        return ai_response
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Brief delay before retry
                    continue
                else:
                    pass  # Try next provider
    
    # Try Azure OpenAI (Option 3)
    if HAS_LLM:
        try:
            endpoint = os.environ.get("AZURE_ENDPOINT")
            azure_key = os.environ.get("AZURE_API_KEY") or os.environ.get("AZURE_KEY")
            if endpoint and azure_key:
                client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(azure_key))
                response = client.complete(
                    messages=[
                        SystemMessage(system_prompt),
                        UserMessage(user_prompt)
                    ],
                    temperature=0.7,
                    top_p=0.95,
                    model="gpt-4o-mini",
                    max_tokens=500
                )
                if response and response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content
        except Exception as e:
            pass  # Silently try fallback

    # Local Heuristic Fallback (Option 4) - Always returns valid response
    herbs_list = ", ".join([h for h, _ in herbal_recommendations[:4]]) if herbal_recommendations else "herbal options"
    drugs_list = ", ".join([d.get("name") for d in drug_recommendations[:4]]) if drug_recommendations else "appropriate medications"
    
    # CRITICAL: Check if Dengue - generate dengue-safe insights
    disease_lower = (disease or "").lower()
    if 'dengue' in disease_lower or 'hemorrhagic' in disease_lower:
        # Dengue-specific safe insights (NO NSAIDs mentioned)
        summary = (
            f"Based on the reported symptoms, suspected {disease} requires immediate medical attention and proper diagnosis. "
            f"\n\n💊 MEDICATION SAFETY FOR DENGUE: For fever and pain relief, Paracetamol (Acetaminophen) is the ONLY safe option. "
            f"NSAIDs such as Aspirin, Ibuprofen, and Diclofenac must be strictly avoided due to increased bleeding risk and potential for hemorrhagic complications. "
            f"These anti-inflammatory drugs can interfere with platelet function, which is already compromised in Dengue fever. "
            f"\n\n🌿 Herbal remedies like {herbs_list} may provide supportive care through immune-boosting and anti-inflammatory properties. "
            f"Traditional herbs such as Papaya leaf extract and Giloy are commonly used in dengue management, though scientific evidence varies. "
            f"These should complement, not replace, medical treatment. "
            f"\n\n🏥 CRITICAL: Dengue requires medical supervision. Adequate hydration (oral rehydration solutions), rest, and monitoring for warning signs "
            f"(severe abdominal pain, persistent vomiting, bleeding gums, blood in stool/vomit, difficulty breathing, restlessness) are essential. "
            f"Seek immediate emergency care if any warning signs develop. Regular monitoring of platelet count and hematocrit is necessary."
        )
    else:
        # Build base summary for non-Dengue conditions
        summary = (
            f"Based on the reported symptoms, {disease} has been identified as the primary concern. "
            f"\n\nHerbal options like {herbs_list} may provide supportive relief through anti-inflammatory and soothing properties. "
            f"These natural remedies work gradually and are often used for long-term management and prevention. "
            f"\n\nPharmaceutical treatments such as {drugs_list} offer evidence-based symptom management with proven efficacy and faster relief. "
            f"These medications are suitable for acute condition management and immediate symptom control. "
            f"\n\nThe optimal approach depends on condition severity, symptom duration, and individual factors. "
            f"Always consult a qualified healthcare professional before starting any treatment. "
            f"Seek immediate medical attention if you experience severe symptoms, difficulty breathing, high fever, or other concerning signs."
        )
    
    # Add special insights for hormonal conditions
    disease_lower = (disease or "").lower()
    if "hormonal" in disease_lower or "pcos" in disease_lower:
        # Added PCOS logic: Enhanced AI insight for hormonal imbalance and cycle regulation
        hormonal_insight = (
            "\n\n💡 HORMONAL DISORDER NOTE: Conditions like PCOS involve hormonal imbalance affecting the menstrual cycle and metabolism. "
            "Cycle regulation is key—lifestyle changes including regular exercise (30+ mins daily), stress management, balanced nutrition with adequate protein, "
            "and consistent sleep (7-9 hrs) are foundational. Herbal remedies support hormonal balance naturally. Always consult an endocrinologist for "
            "hormone level testing, diagnosis confirmation, and personalized treatment including possible medications like metformin or hormonal contraceptives."
        )
        summary += hormonal_insight
    elif "menorrhagia" in disease_lower or "heavy" in disease_lower and "bleed" in disease_lower:
        # Added Menorrhagia logic: Enhanced AI insight for heavy menstrual bleeding and iron loss
        menorrhagia_insight = (
            "\n\n💡 MENORRHAGIA NOTE: Heavy or prolonged menstrual bleeding can lead to significant iron loss and anemia. Symptoms like weakness and dizziness "
            "may indicate low iron levels. Iron-rich herbal remedies can help replenish stores. Pharmaceutical options often include iron supplements, "
            "tranexamic acid (to reduce bleeding), or hormonal treatments (contraceptives/progestins) to regulate flow. Monitor your symptoms closely—if bleeding "
            "exceeds normal duration/volume or symptoms worsen, seek urgent medical evaluation. Regular iron level testing (ferritin/hemoglobin) is essential."
        )
        summary += menorrhagia_insight
    
    return summary

# ------------------------------------------------------------------------------------
# Format results for terminal display (keeps original formatting style but simplified)
# ------------------------------------------------------------------------------------
def format_answer_for_display(response: Dict) -> str:
    """Format the comprehensive response for user display with herbs and drugs (rich terminal)."""
    # reuse dictionaries defined above
    global spelling_map, condition_info, severity_icons, availability_icons

    # Defensive defaults
    spelling_map_local = spelling_map or {}
    condition_info_local = condition_info or {}
    severity_local = severity_icons or {}
    availability_local = availability_icons or {}

    # Spelling check
    user_input = (response.get("input") or "").lower()
    spelling_issues = []
    for typo, correct in spelling_map_local.items():
        if typo and typo in user_input:
            spelling_issues.append((typo, correct))

    # Header
    answer_lines = []
    answer_lines.append("╔" + "═" * 78 + "╗")
    answer_lines.append("║" + " " * 78 + "║")
    title = f"    {BOLD}🏥 AI-POWERED HEALTH RECOMMENDATION SYSTEM 🌿{RESET}"
    subtitle = f"{BOLD}Comprehensive Herbal & Pharmaceutical Guide{RESET}"
    # center
    answer_lines.append("║" + title.center(78) + "║")
    answer_lines.append("║" + subtitle.center(78) + "║")
    answer_lines.append("║" + " " * 78 + "║")
    answer_lines.append("╚" + "═" * 78 + "╝\n")

    # Spelling section
    if spelling_issues:
        answer_lines.append(f"{YELLOW}{BOLD}✏️  SPELLING CHECK{RESET}")
        answer_lines.append(f"{YELLOW}" + "━" * 78 + f"{RESET}\n")
        answer_lines.append(f"  {YELLOW}⚠️  We detected some spelling variations in your input:{RESET}")
        for typo, correct in spelling_issues:
            answer_lines.append(f"     • \"{YELLOW}{typo}{RESET}\" → should be \"{GREEN}{correct}{RESET}\"")
        answer_lines.append("  " + f"{BOLD}💡 Tip:{RESET} Use correct spelling for more accurate results.")
        answer_lines.append("")

    # Symptom analysis
    answer_lines.append(f"{BLUE}{BOLD}📋 SYMPTOM ANALYSIS{RESET}")
    answer_lines.append(f"{BLUE}" + "━" * 78 + f"{RESET}\n")
    answer_lines.append(f"  📝 Your Input: \"{response.get('input')}\"")
    
    # Show diagnosis source if available (Advanced vs Basic)
    diagnosis_source = response.get('diagnosis_source', '')
    source_label = ""
    if diagnosis_source == 'advanced':
        source_label = f" {BLUE}(Advanced Diagnosis){RESET}"
    elif diagnosis_source == 'basic':
        source_label = f" {YELLOW}(Basic Diagnosis){RESET}"
    
    answer_lines.append(f"  🧠 {BOLD}Detected Condition:{RESET} {GREEN}{response.get('detected_disease')}{RESET}{source_label}")
    
    # Confidence interpret with better messaging
    conf = float(response.get('confidence', 0.0))
    conf_pct = conf * 100.0
    conf_word = "Low"
    conf_color = YELLOW
    
    if conf_pct >= 80:
        conf_word = "High"
        conf_color = GREEN
    elif conf_pct >= 60:
        conf_word = "Moderate"
        conf_color = YELLOW
    else:
        conf_word = "Low"
        conf_color = RED
    
    answer_lines.append(f"     {BOLD}Confidence Level:{RESET} {conf_color}{conf_pct:.1f}% ({conf_word}){RESET}")
    
    # Low confidence warning
    if conf_pct < 40:
        answer_lines.append(f"     {RED}{BOLD}⚠️  LOW CONFIDENCE WARNING:{RESET}")
        answer_lines.append(f"     {RED}Symptoms are vague or ambiguous. Recommendations are limited.{RESET}")
        answer_lines.append(f"     {RED}Please provide more specific symptoms or consult a doctor.{RESET}")
    elif conf_pct < 60:
        answer_lines.append(f"     {YELLOW}ℹ️  Moderate confidence - consider providing more details for better results.{RESET}")
    
    # Disease-specific typical symptoms (medical accuracy)
    detected_disease = response.get('detected_disease', '').lower()
    disease_symptoms_map = {
        'dengue': 'High fever (104°F+), severe headache, joint/muscle pain, eye pain, rash',
        'malaria': 'Intermittent fever, chills, sweating, headache, nausea, vomiting',
        'typhoid': 'Sustained fever, weakness, abdominal pain, headache, loss of appetite',
        'migraine': 'Severe throbbing headache (one side), nausea, light/sound sensitivity',
        'influenza': 'High fever, body aches, fatigue, dry cough, sore throat',
        'pneumonia': 'Cough with phlegm, fever, chest pain, difficulty breathing',
        'covid-19': 'Fever, dry cough, fatigue, loss of taste/smell, breathing difficulty',
        'diabetes': 'Increased thirst, frequent urination, fatigue, blurred vision, slow healing'
    }
    
    # Try to find matching disease-specific symptoms
    typical_symptoms = None
    for disease_key, symptoms in disease_symptoms_map.items():
        if disease_key in detected_disease:
            typical_symptoms = symptoms
            break
    
    # Fallback to generic symptom if available
    if not typical_symptoms and response.get("disease_symptom"):
        typical_symptoms = response.get('disease_symptom')
    
    if typical_symptoms:
        answer_lines.append(f"     {BOLD}Typical Symptoms:{RESET} {typical_symptoms}")
    answer_lines.append("")

    # Condition description
    answer_lines.append(f"{BLUE}{BOLD}📌 ABOUT YOUR CONDITION{RESET}")
    answer_lines.append(f"{BLUE}" + "━" * 78 + f"{RESET}")
    disease_name = response.get('detected_disease', '')
    disease_key = None
    try:
        disease_key = next((k for k in condition_info_local.keys() if k.lower() in disease_name.lower()), None)
    except Exception:
        disease_key = None
    if disease_key:
        for line in condition_info_local[disease_key]:
            answer_lines.append(line)
    else:
        answer_lines.append(f"  {disease_name} is a medical condition requiring attention.")
        answer_lines.append("  Please consult a healthcare professional for proper diagnosis and treatment.")
    answer_lines.append("")

    # Allergy warnings
    allergy_warnings = response.get("allergy_warnings", [])
    if allergy_warnings:
        answer_lines.append(f"{RED}{BOLD}🚨 ALLERGY ALERTS{RESET}")
        answer_lines.append(f"{RED}" + "━" * 78 + f"{RESET}")
        for warning in allergy_warnings:
            sev = warning.get('severity', 'MODERATE')
            icon = severity_local.get(sev, '🟡')
            answer_lines.append(f"  {icon} {RED}{BOLD}{warning['drug']}{RESET} - {warning['allergen']} allergy")
            answer_lines.append(f"     Severity: {RED}{sev}{RESET}")
            answer_lines.append(f"     ⚠️  {BOLD}DO NOT USE – Use safe alternative instead{RESET}")
        answer_lines.append("")

    # Drug interactions
    drug_interactions = response.get("drug_interactions", [])
    if drug_interactions:
        answer_lines.append(f"{RED}{BOLD}⚠️  DRUG INTERACTION WARNINGS{RESET}")
        answer_lines.append(f"{RED}" + "━" * 78 + f"{RESET}")
        for interaction in drug_interactions:
            sev = interaction.get('severity', 'MODERATE')
            icon = severity_local.get(sev, '🟡')
            answer_lines.append(f"  {icon} {BOLD}{interaction['drug1']} + {interaction['drug2']}{RESET}")
            answer_lines.append(f"     Severity: {sev}")
            answer_lines.append(f"     Effect: {interaction.get('effect')}")
            answer_lines.append(f"     Recommendation: {interaction.get('recommendation')}")
        answer_lines.append("")

    # Emergency signs (NEW - for menstrual and other serious conditions)
    emergency_signs = response.get("emergency_signs", [])
    if emergency_signs:
        answer_lines.append(f"{RED}{BOLD}🚨 EMERGENCY WARNING SIGNS{RESET}")
        answer_lines.append(f"{RED}" + "━" * 78 + f"{RESET}")
        answer_lines.append(f"  {RED}{BOLD}SEEK IMMEDIATE MEDICAL ATTENTION IF YOU EXPERIENCE:{RESET}")
        for sign in emergency_signs:
            answer_lines.append(f"  {RED}⚠️  {sign}{RESET}")
        answer_lines.append("")

    # Herbal recommendations
    herbal_recs = response.get("herbal_recommendations", [])
    if herbal_recs:
        answer_lines.append(f"{GREEN}{BOLD}🌿 HERBAL INGREDIENTS ({len(herbal_recs)}){RESET}")
        
        # Show message if recommendations were limited due to low confidence
        conf = float(response.get('confidence', 0.0))
        if conf < 0.40:
            answer_lines.append(f"{GREEN}" + "━" * 78 + f"{RESET}")
            answer_lines.append(f"  {YELLOW}ℹ️  Limited recommendations due to low confidence{RESET}")
        
        answer_lines.append(f"{GREEN}" + "━" * 78 + f"{RESET}")
        for i, rec in enumerate(herbal_recs, 1):
            score = float(rec.get('relevance_score', 0.0))
            bar_len = max(0, min(30, int(round(score * 30))))
            bar = "█" * bar_len + "░" * (30 - bar_len)
            answer_lines.append(f"  {BOLD}{i}. {rec.get('ingredient').upper()}{RESET}")
            answer_lines.append(f"     Relevance: {GREEN}{bar}{RESET} {score:.1%}")
            
            # Show effectiveness rating if available from datasets
            if rec.get('effectiveness_rating'):
                eff = rec['effectiveness_rating']
                evidence = rec.get('evidence_level', 'Unknown')
                eff_bar_len = max(0, min(30, int(round(eff * 30))))
                eff_bar = "█" * eff_bar_len + "░" * (30 - eff_bar_len)
                answer_lines.append(f"     Clinical:  {BLUE}{eff_bar}{RESET} {eff:.1%} ({evidence} evidence)")
            
            answer_lines.append(f"     Benefits:  {rec.get('benefits')}")
            if rec.get("active_compounds"):
                answer_lines.append(f"     Compounds: {rec.get('active_compounds')}")
            answer_lines.append(f"     Usage:     {rec.get('usage')}")
        answer_lines.append("")

    # Drug recommendations
    drug_recs = response.get("drug_recommendations", [])
    if drug_recs:
        answer_lines.append(f"{YELLOW}{BOLD}💊 PHARMACEUTICAL MEDICATIONS ({len(drug_recs)}){RESET}")
        
        # Show message if recommendations were limited due to low confidence
        conf = float(response.get('confidence', 0.0))
        if conf < 0.40:
            answer_lines.append(f"{YELLOW}" + "━" * 78 + f"{RESET}")
            answer_lines.append(f"  {YELLOW}ℹ️  Limited recommendations due to low confidence{RESET}")
        
        # Dengue-specific NSAID warning (CRITICAL SAFETY)
        detected_disease = response.get('detected_disease', '').lower()
        if 'dengue' in detected_disease:
            answer_lines.append(f"{RED}{BOLD}" + "━" * 78 + f"{RESET}")
            answer_lines.append(f"  {RED}{BOLD}⚠️  DENGUE SAFETY WARNING:{RESET}")
            answer_lines.append(f"  {RED}• Avoid Aspirin and NSAIDs (Ibuprofen, Diclofenac) - bleeding risk{RESET}")
            answer_lines.append(f"  {RED}• Use Paracetamol ONLY under medical supervision{RESET}")
            answer_lines.append(f"  {RED}• Seek immediate medical care for proper diagnosis and monitoring{RESET}")
            answer_lines.append(f"{RED}{BOLD}" + "━" * 78 + f"{RESET}")
        
        answer_lines.append(f"{YELLOW}" + "━" * 78 + f"{RESET}")
        for i, drug in enumerate(drug_recs, 1):
            drug_name = drug.get('name', '').upper()
            
            # Backup safety check: Mark NSAIDs with ❌ if somehow present for dengue
            nsaid_names = ['aspirin', 'ibuprofen', 'diclofenac', 'naproxen', 'indomethacin', 'ketorolac', 'mefenamic']
            is_nsaid = any(nsaid in drug_name.lower() for nsaid in nsaid_names)
            is_dengue = 'dengue' in detected_disease.lower() or 'hemorrhagic' in detected_disease.lower()
            
            if is_nsaid and is_dengue:
                # Show NSAID with explicit contraindication marker
                answer_lines.append(f"  {BOLD}{i}. {drug_name} {RED}❌ NOT RECOMMENDED FOR DENGUE{RESET}")
            else:
                # Display drug normally (NSAIDs already filtered for Dengue)
                answer_lines.append(f"  {BOLD}{i}. {drug_name}{RESET}")
            
            avail = drug.get('availability', 'Unknown')
            avail_icon = availability_local.get(avail, '🟡')
            
            # Show safety warning if present
            safety_warning = drug.get('safety_warning')
            if safety_warning:
                answer_lines.append(f"     {RED}{BOLD}{safety_warning}{RESET}")
            
            brand_names = ", ".join(drug.get('brand_names', [])) if drug.get('brand_names') else "—"
            answer_lines.append(f"     {BOLD}Brand Names:{RESET}  {brand_names}")
            answer_lines.append(f"     {BOLD}Type:{RESET}         {drug.get('type', '—')}")
            answer_lines.append(f"     {BOLD}Dosage:{RESET}       {drug.get('dosage', '—')}")
            answer_lines.append(f"     {BOLD}Purpose:{RESET}      {drug.get('purpose', '—')}")
            
            # Show user ratings if available from dataset integration
            if drug.get('user_rating'):
                rating_stars = "⭐" * int(round(drug['user_rating']))
                answer_lines.append(f"     {BOLD}User Rating:{RESET}  {rating_stars} {drug['user_rating']:.1f}/5 ({drug.get('review_count', 0)} reviews)")
            if drug.get('user_effectiveness'):
                answer_lines.append(f"     {BOLD}User Reports:{RESET} {drug['user_effectiveness']} find it effective")
            
            answer_lines.append(f"     {BOLD}Availability:{RESET} {avail_icon} {avail}")
            answer_lines.append(f"     {BOLD}Price Range:{RESET}  {YELLOW}{drug.get('price_range', '—')}{RESET}")
            answer_lines.append(f"     {BOLD}Side Effects:{RESET} {RED}{drug.get('side_effects', '—')}{RESET}")
        answer_lines.append("")

    # Comparison section
    if herbal_recs and drug_recs:
        answer_lines.append(f"{HEADER}{BOLD}🔄 COMPARISON: HERBAL vs PHARMACEUTICAL{RESET}")
        answer_lines.append(f"{HEADER}" + "━" * 78 + f"{RESET}")
        answer_lines.append("  ✓ Natural ingredients                ✓ Clinically proven")
        answer_lines.append("  ✓ Fewer synthetic additives          ✓ Faster symptom relief")
        answer_lines.append("  ✓ Milder with fewer side effects     ✓ Precise dosing")
        answer_lines.append("  ✓ Long-term preventive care          ✓ Well-researched effects")
        answer_lines.append("  ✗ Slower acting                       ✗ More pronounced side effects")
        answer_lines.append("  ✗ Quality varies by brand             ✗ May require prescription")
        answer_lines.append("")
        answer_lines.append(f"  {BOLD}{BLUE}💡 SMART RECOMMENDATION:{RESET}")
        
        # Disease-specific recommendations (medically accurate guidance)
        detected_disease = response.get('detected_disease', '').lower()
        
        if 'dengue' in detected_disease or 'hemorrhagic' in detected_disease:
            answer_lines.append(f"     • {RED}{BOLD}Suspected Dengue:{RESET} Use Paracetamol ONLY, avoid all NSAIDs")
            answer_lines.append("     • Seek immediate medical care for proper diagnosis")
            answer_lines.append("     • Monitor for warning signs: bleeding, severe abdominal pain")
        
        elif 'covid' in detected_disease or 'coronavirus' in detected_disease:
            answer_lines.append(f"     • {BLUE}{BOLD}Suspected COVID-19:{RESET} Isolate immediately, get tested")
            answer_lines.append("     • Use Paracetamol for fever, monitor oxygen levels if possible")
            answer_lines.append("     • Seek care if breathing difficulty or persistent symptoms")
        
        elif 'malaria' in detected_disease:
            answer_lines.append(f"     • {RED}{BOLD}Suspected Malaria:{RESET} Requires immediate medical diagnosis (blood test)")
            answer_lines.append("     • Prescription antimalarial drugs are essential - do not self-medicate")
            answer_lines.append("     • Herbal remedies cannot cure malaria, only support symptom management")
        
        elif 'diabetes' in detected_disease or 'hyperglycemia' in detected_disease:
            answer_lines.append(f"     • {YELLOW}{BOLD}Diabetes Management:{RESET} Requires medical evaluation and blood glucose monitoring")
            answer_lines.append("     • Lifestyle changes (diet, exercise) are critical along with medication")
            answer_lines.append("     • Herbal support should complement, not replace, prescribed treatments")
        
        elif 'hypertension' in detected_disease or 'high blood pressure' in detected_disease:
            answer_lines.append(f"     • {YELLOW}{BOLD}Blood Pressure Management:{RESET} Medical evaluation needed")
            answer_lines.append("     • Lifestyle modifications essential: low sodium diet, regular exercise")
            answer_lines.append("     • Prescription medications may be required for control")
        
        elif 'asthma' in detected_disease:
            answer_lines.append(f"     • {BLUE}{BOLD}Asthma Management:{RESET} Keep rescue inhaler accessible at all times")
            answer_lines.append("     • Identify and avoid triggers (allergens, smoke, cold air)")
            answer_lines.append("     • Controller medications required for persistent asthma")
        
        elif 'typhoid' in detected_disease or 'bacterial infection' in detected_disease:
            answer_lines.append("     • Suspected Bacterial Infection: Requires medical diagnosis and antibiotics")
            answer_lines.append("     • Herbal support may complement medical treatment")
            answer_lines.append("     • Do not delay professional medical care")
        
        else:
            # Generic recommendations for mild/common conditions
            answer_lines.append("     • Acute Conditions: Start with pharmaceutical options")
            answer_lines.append("     • Chronic Prevention: Consider herbal remedies")
            answer_lines.append("     • Optimal Approach: Combination therapy (consult doctor)")
        
        answer_lines.append("")

    # AI insights
    if response.get("ai_insights"):
        answer_lines.append(f"{HEADER}{BOLD}🤖 AI-GENERATED INSIGHTS{RESET}")
        answer_lines.append(f"{HEADER}" + "━" * 78 + f"{RESET}")
        answer_lines.append(response.get("ai_insights"))
        answer_lines.append("")

    # Footer disclaimer
    answer_lines.append(f"{RED}{BOLD}╔" + "═" * 78 + "╗{RESET}".replace("{RESET}", RESET))
    answer_lines.append(f"{RED}{BOLD}║ ⚠️  IMPORTANT DISCLAIMER{RESET}".replace("{RESET}", RESET))
    answer_lines.append(f"{RED}{BOLD}╠" + "═" * 78 + "╣{RESET}".replace("{RESET}", RESET))
    answer_lines.append(f"{RED}║ This is for EDUCATIONAL PURPOSES ONLY. This system provides general information and should NOT replace professional medical advice.{RESET}")
    answer_lines.append(f"{RED}║ ALWAYS consult qualified healthcare professionals before starting any herbal treatment, taking new medications, combining herbs & drugs, or making dietary changes.{RESET}")
    answer_lines.append(f"{RED}║ 🚨 IN CASE OF EMERGENCY: Seek immediate medical attention{RESET}")
    answer_lines.append(f"{RED}{BOLD}╚" + "═" * 78 + "╝{RESET}".replace("{RESET}", RESET))

    # join with newline
    return "\n".join(answer_lines)

# ------------------------------------------------------------------------------------
# Main orchestrator: generate_comprehensive_answer (keeps original logic)
# ------------------------------------------------------------------------------------
def generate_comprehensive_answer(
    user_input: str,
    knowledge: Dict,
    use_ai: bool = True,
    include_drugs: bool = True,
    user_allergies: Set[str] = None
) -> Dict:
    """
    Generate a comprehensive answer to user's health query.
    Combines disease prediction, herbal recommendations, drug recommendations, and AI insights.
    """
    # Step 1: Predict disease using improved detection v2 as primary method
    enhanced_result = None
    try:
        # PRIORITY: Use detect_condition_v2 first for accurate menstrual/hormonal detection
        disease, confidence = detect_condition_v2(user_input)
        
        # If USE_ENHANCED, also try enhanced predictor for additional context (menstrual/PCOS patterns)
        if USE_ENHANCED:
            try:
                enhanced_result = predict_disease_enhanced(user_input)
            except Exception:
                enhanced_result = None
    except Exception:
        # Fallback to enhanced predictor if available
        try:
            if USE_ENHANCED:
                enhanced_result = predict_disease_enhanced(user_input)
                disease = enhanced_result.get('primary_disease')
                confidence = float(enhanced_result.get('confidence', 0.0))
            else:
                predicted = predict_disease(user_input)
                if isinstance(predicted, tuple):
                    disease, confidence = predicted
                else:
                    disease = predicted
                    confidence = 0.5
        except Exception:
            disease, confidence = ("General Symptom", 0.5)

    # Step 2: Get herbal recommendations (limit for low confidence)
    # If enhanced predictor has herbal_remedies, use those; otherwise get from knowledge base
    max_herbs = 5 if confidence >= 0.40 else 3  # Reduce recommendations for low confidence
    
    if enhanced_result and enhanced_result.get('herbal_remedies'):
        # Use herbal remedies from menstrual/specialized pattern detection
        enhanced_herbal = enhanced_result.get('herbal_remedies', [])
        herbal_recommendations = [(r['name'], 0.85) for r in enhanced_herbal[:max_herbs]]
    else:
        # Fall back to knowledge base lookup
        herbal_recommendations = suggest_ingredients_for_disease(disease, knowledge=knowledge)
        herbal_recommendations = herbal_recommendations[:max_herbs]

    # Step 3: Get pharma recommendations if enabled (limit for low confidence)
    drug_recommendations = []
    drug_interactions = []
    allergy_warnings = []
    
    max_drugs = 5 if confidence >= 0.40 else 3  # Reduce recommendations for low confidence

    if include_drugs:
        # If enhanced predictor has pharma_options, use those; otherwise get from knowledge base
        if enhanced_result and enhanced_result.get('pharma_options'):
            # Use pharma options from menstrual/specialized pattern detection
            enhanced_drugs = enhanced_result.get('pharma_options', [])
            drug_recommendations = [
                {
                    'name': d['name'],
                    'use': d['use'],
                    'brand_names': d.get('brand_names', []),
                    'type': 'Specialized Medication',
                    'dosage': 'Consult healthcare provider',
                    'purpose': d['use'],
                    'availability': 'Common - Medical Store',
                    'price_range': 'Variable',
                    'side_effects': 'Consult healthcare provider'
                }
                for d in enhanced_drugs
            ]
        else:
            # Fall back to knowledge base lookup
            drug_recommendations = suggest_drugs_for_disease(disease, top_n=max_drugs)
        
        # Add safety warnings to drugs
        for drug in drug_recommendations:
            drug_name = drug.get('name', '')
            if drug_name in DRUG_SAFETY_WARNINGS:
                drug['safety_warning'] = DRUG_SAFETY_WARNINGS[drug_name]
            else:
                drug['safety_warning'] = None
            
            # Enhance with user review data from integrator if available
            if HAS_INTEGRATOR:
                try:
                    integrator = get_integrator()
                    review_data = integrator.get_drug_effectiveness(drug_name, disease)
                    if review_data:
                        drug['user_rating'] = review_data['average_rating']
                        drug['user_effectiveness'] = f"{review_data['average_effectiveness']:.0%}"
                        drug['review_count'] = review_data['review_count']
                except Exception:
                    pass
        
        # Limit drug list for low confidence
        drug_recommendations = drug_recommendations[:max_drugs]
        
        # CRITICAL: Filter out NSAIDs completely for Dengue (don't show them at all)
        disease_lower = disease.lower()
        if 'dengue' in disease_lower or 'hemorrhagic' in disease_lower:
            nsaid_list = ['aspirin', 'ibuprofen', 'diclofenac', 'naproxen', 'ketoprofen', 'indomethacin']
            drug_recommendations = [
                drug for drug in drug_recommendations 
                if not any(nsaid in drug.get('name', '').lower() for nsaid in nsaid_list)
            ]
        
        drug_names = [d.get('name', '') for d in drug_recommendations]
        interactions_db = load_drug_interactions()
        drug_interactions = check_drug_interactions(drug_names, interactions_db)
        if user_allergies:
            allergy_warnings = check_allergies(drug_recommendations, user_allergies)

    # Build response
    response = {
        "input": user_input,
        "detected_disease": disease,
        "confidence": float(confidence),
        "herbal_recommendations": [],
        "drug_recommendations": drug_recommendations,
        "drug_interactions": drug_interactions,
        "allergy_warnings": allergy_warnings,
        "ai_insights": None,
        "emergency_signs": enhanced_result.get('emergency_signs', []) if enhanced_result else []
    }

    # Enrich herbal recs with compound-to-herb mapping
    herbs_df = knowledge.get("herbs", SAMPLE_HERBS)
    for ingredient, score in herbal_recommendations:
        herb_info = get_herb_info(ingredient, herbs_df)
        
        # Map chemical compound to parent herb if needed
        ingredient_lower = ingredient.lower()
        parent_herb = COMPOUND_TO_HERB.get(ingredient_lower, None)
        
        if parent_herb:
            # This is a compound, show parent herb
            display_name = f"{parent_herb} ({ingredient})"
        else:
            # This is already a herb name
            display_name = ingredient
        
        herb_rec = {
            "ingredient": display_name,
            "original_name": ingredient,
            "relevance_score": float(score),
            "benefits": herb_info.get("benefits", "Traditional herbal remedy") if isinstance(herb_info, dict) else "Traditional herbal remedy",
            "active_compounds": herb_info.get("active_compounds", "") if isinstance(herb_info, dict) else "",
            "usage": herb_info.get("usage", "Consult herbalist for dosage") if isinstance(herb_info, dict) else "Consult herbalist for dosage"
        }
        
        # Enhance with dataset integrator if available
        if HAS_INTEGRATOR:
            try:
                integrator = get_integrator()
                effectiveness = integrator.get_herb_effectiveness(ingredient)
                if effectiveness:
                    herb_rec['effectiveness_rating'] = effectiveness
                    herb_rec['evidence_level'] = 'High' if effectiveness > 0.8 else 'Moderate' if effectiveness > 0.6 else 'Low'
            except Exception:
                pass
        
        response["herbal_recommendations"].append(herb_rec)

    # Disease context from knowledge base (if available)
    disease_info = None
    try:
        ds = knowledge.get("diseases", [])
        if pd is not None and hasattr(ds, "iterrows"):
            found = ds[ds["disease"].str.lower() == (disease or "").lower()]
            if not found.empty:
                disease_info = found.iloc[0]
        else:
            # list fallback
            for r in ds:
                if str(r.get("disease", "")).lower() == (disease or "").lower():
                    disease_info = r
                    break
    except Exception:
        disease_info = None

    if disease_info is not None:
        # symptom may be present as column or key
        if isinstance(disease_info, dict):
            response["disease_symptom"] = disease_info.get("symptom", "")
        else:
            try:
                response["disease_symptom"] = disease_info.get("symptom", "")
            except (AttributeError, TypeError):
                response["disease_symptom"] = ""

    # AI insights - use disease-specific templates based on detected_disease
    if use_ai:
        detected_disease = response["detected_disease"]
        response["ai_insights"] = generate_ai_insights(
            user_input, 
            detected_disease,  # Pass the actual detected disease name
            herbal_recommendations, 
            drug_recommendations, 
            knowledge
        )

    return response

# ------------------------------------------------------------------------------------
# Logging helper
# ------------------------------------------------------------------------------------
LOG_FILE = "assistant_interactions.jsonl"

def log_interaction(entry: Dict):
    """Append an entry to LOG_FILE in JSON lines format."""
    try:
        entry_copy = dict(entry)
        entry_copy["_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry_copy, ensure_ascii=False) + "\n")
    except Exception:
        pass

# ------------------------------------------------------------------------------------
# Main interactive terminal UI
# ------------------------------------------------------------------------------------
def main():
    # Load knowledge base
    print("🏥 Welcome to Dual Recommendation Health Assistant!")
    print("   (Herbal Remedies + Pharmaceutical Medications)")
    print("=" * 66)
    print("📚 Loading medical knowledge base...")
    knowledge = load_knowledge_base()
    print("✅ Knowledge base loaded!")
    print("💊 Pharmaceutical database " + ("available!" if HAS_DRUG_DB else "(fallback sample used)"))
    print()
    if HAS_LLM:
        print("✅ AI LLM enabled (environment configured)")
    else:
        print("⚠️  AI LLM not available — using heuristic fallback for AI insights.")
    print("\n" + "=" * 66 + "\n")
    print(f"{YELLOW}💡 TIP:{RESET} For best results, enter symptoms simply (e.g., 'fever', 'headache', 'loose motions')")
    print("\n" + "=" * 66 + "\n")

    # Greet and optional TTS
    speak_text("Welcome to the Dual Recommendation Health Assistant. Enter your symptoms or type quit to exit.")

    try:
        while True:
            user_input = input("🧍 Enter your problem or symptoms (or 'quit' to exit): ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("Goodbye — stay healthy!")
                speak_text("Goodbye. Stay healthy.")
                break

            # optional allergy input prompt
            allergy_input = input("⚠️  Any allergies? (comma separated or press Enter): ").strip()
            user_allergies = set([a.strip() for a in allergy_input.split(",") if a.strip()]) if allergy_input else None

            print("\n🔍 Analyzing your symptoms...\n")
            response = generate_comprehensive_answer(user_input, knowledge, use_ai=True, include_drugs=True, user_allergies=user_allergies)

            # format and display
            display = format_answer_for_display(response)
            print(display)

            # TTS short summary
            tts_short = f"Detected condition: {response.get('detected_disease')}. Confidence {response.get('confidence')*100:.0f} percent."
            speak_text(tts_short)

            # log
            log_entry = {
                "input": user_input,
                "detected_disease": response.get("detected_disease"),
                "confidence": response.get("confidence"),
                "herbal_recommendations": [h.get("ingredient") for h in response.get("herbal_recommendations", [])],
                "drug_recommendations": [d.get("name") for d in response.get("drug_recommendations", [])],
                "allergy_warnings": response.get("allergy_warnings", []),
                "drug_interactions": response.get("drug_interactions", [])
            }
            log_interaction(log_entry)

            # ask to show JSON
            show_json = input("\n📊 Show detailed JSON response? (y/n): ").strip().lower()
            if show_json in ("y", "yes"):
                print(json.dumps(response, indent=2, ensure_ascii=False))

            print("\n" + "=" * 66 + "\n")

    except KeyboardInterrupt:
        print("\nExiting — take care.")
        speak_text("Exiting. Take care.")

if __name__ == "__main__":
    main()