"""
Cure-Blend: AI-Powered Health Recommendation System
Professional Streamlit Web Application v3.0

Copyright (c) 2026 vishwaksen21
All Rights Reserved - Proprietary Software
"""

import streamlit as st
import sys
import os
import json
from typing import Optional, Dict, List

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# --------------------------------------------------
# Helper Functions for Confidence Improvement
# --------------------------------------------------

# Diagnostic symptom patterns - highly specific symptoms that strongly indicate certain diseases
DIAGNOSTIC_SYMPTOMS = {
    "dengue": [
        "severe headache", "pain behind eyes", "retro-orbital pain", "eye pain",
        "severe body ache", "joint pain", "bone pain", "breakbone fever",
        "rash", "petechiae", "bleeding gums", "nose bleed"
    ],
    "malaria": [
        "periodic fever", "cyclic fever", "fever cycles", "chills and sweating",
        "rigors", "shivering", "sweating episodes", "fever spikes"
    ],
    "uti": [
        "burning urination", "dysuria", "painful urination", "burning sensation when urinating",
        "frequent urination", "urgency", "cloudy urine", "bloody urine", "lower abdominal pain"
    ],
    "covid": [
        "loss of smell", "anosmia", "loss of taste", "ageusia",
        "dry cough", "persistent cough", "shortness of breath"
    ],
    "typhoid": [
        "sustained fever", "step-ladder fever", "rose spots", "abdominal pain",
        "relative bradycardia", "constipation followed by diarrhea"
    ],
    "pneumonia": [
        "productive cough", "chest pain when breathing", "pleuritic chest pain",
        "shortness of breath", "rapid breathing", "difficulty breathing"
    ],
    "migraine": [
        "unilateral headache", "one-sided headache", "throbbing headache", "pulsating headache",
        "sensitivity to light", "photophobia", "nausea with headache", "visual aura"
    ],
    "appendicitis": [
        "right lower quadrant pain", "mcburney's point pain", "rebound tenderness",
        "pain that moves to right lower abdomen", "pain worsens with movement"
    ],
    "strep throat": [
        "severe sore throat", "difficulty swallowing", "white patches on tonsils",
        "swollen tonsils", "tender neck lymph nodes", "no cough"
    ],
    "flu": [
        "sudden onset fever", "severe body aches", "extreme fatigue",
        "dry cough", "chills", "sweats"
    ]
}

# Disease name aliases for matching
DISEASE_ALIASES = {
    "urinary tract infection": "uti",
    "urinary infection": "uti",
    "bladder infection": "uti",
    "covid-19": "covid",
    "coronavirus": "covid",
    "sars-cov-2": "covid",
    "influenza": "flu",
    "common cold": "cold",
    "pharyngitis": "strep throat"
}

def count_diagnostic_symptoms(symptoms: str, disease: str) -> int:
    """Count how many diagnostic symptoms are present"""
    symptoms_lower = symptoms.lower()
    disease_lower = disease.lower()
    
    # Apply disease aliases
    disease_lower = DISEASE_ALIASES.get(disease_lower, disease_lower)
    
    count = 0
    if disease_lower in DIAGNOSTIC_SYMPTOMS:
        for diagnostic_symptom in DIAGNOSTIC_SYMPTOMS[disease_lower]:
            if diagnostic_symptom in symptoms_lower:
                count += 1
    
    return count

def calibrate_confidence(raw_confidence: float, symptoms: str, disease: str, 
                        structured_data: dict) -> float:
    """Calibrate confidence based on symptom quality and diagnostic markers"""
    # Guard against missing structured data
    structured_data = structured_data or {}
    
    calibrated = raw_confidence
    
    # Boost 1: Diagnostic symptoms present
    diagnostic_count = count_diagnostic_symptoms(symptoms, disease)
    if diagnostic_count >= 3:
        calibrated += 0.15  # Strong boost for 3+ diagnostic symptoms
    elif diagnostic_count == 2:
        calibrated += 0.10  # Medium boost
    elif diagnostic_count == 1:
        calibrated += 0.05  # Small boost
    
    # Boost 2: Duration specified (shows patient is providing detail)
    duration = structured_data.get('duration', 'Not specified')
    if duration != 'Not specified':
        calibrated += 0.05
    
    # Boost 3: High severity with specific symptoms (usually more accurate)
    severity = structured_data.get('severity_level', 5)
    symptom_count = len(symptoms.split())
    if severity >= 7 and symptom_count >= 5:
        calibrated += 0.08
    
    # Boost 4: Multiple structured symptoms checked (better quality data)
    checked_count = sum([
        structured_data.get('fever', False),
        structured_data.get('cough', False),
        structured_data.get('headache', False),
        structured_data.get('fatigue', False),
        structured_data.get('body_pain', False),
        structured_data.get('nausea', False),
        structured_data.get('breathing', False),
        structured_data.get('rash', False),
        structured_data.get('diarrhea', False),
        structured_data.get('vomiting', False)
    ])
    if checked_count >= 4:
        calibrated += 0.10
    elif checked_count >= 2:
        calibrated += 0.05
    
    # Penalty: Very vague symptoms (< 3 words)
    if symptom_count < 3:
        calibrated -= 0.10
    
    # Cap boost to prevent inflating weak diagnoses
    max_boost = raw_confidence * 0.6  # Max 60% relative increase
    if calibrated > raw_confidence:
        calibrated = min(raw_confidence + max_boost, calibrated)
    
    # Cap at 0.95 (never claim 100% certainty) and floor at 0.05
    calibrated = max(0.05, min(0.95, calibrated))
    
    return calibrated

def normalize_symptoms(text: str) -> str:
    """Normalize symptom text for better matching"""
    text = text.lower().strip()
    
    # Common misspellings and synonyms
    replacements = {
        "temp": "fever", "temperature": "fever", "high temp": "high fever",
        "ache": "pain", "aches": "pain", "aching": "pain",
        "tired": "fatigue", "exhausted": "fatigue", "weakness": "fatigue",
        "throw up": "vomiting", "throwing up": "vomiting", "puke": "vomiting",
        "pee": "urination", "peeing": "urination", "urinate": "urination",
        "dizzy": "dizziness", "lightheaded": "dizziness",
        "stuffy nose": "nasal congestion", "blocked nose": "nasal congestion",
        "runny nose": "rhinorrhea", "sore throat": "pharyngitis",
        "chest pain": "thoracic pain", "stomach pain": "abdominal pain",
        "belly pain": "abdominal pain", "tummy ache": "abdominal pain"
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    return text

def enhance_symptoms_with_context(symptoms: str, structured_data: dict) -> str:
    """Add structured context to improve confidence"""
    enhanced = normalize_symptoms(symptoms)
    
    # Add checked symptoms
    checked_symptoms = []
    if structured_data.get('fever'): checked_symptoms.append('fever')
    if structured_data.get('cough'): checked_symptoms.append('cough')
    if structured_data.get('headache'): checked_symptoms.append('headache')
    if structured_data.get('fatigue'): checked_symptoms.append('fatigue')
    if structured_data.get('body_pain'): checked_symptoms.append('body pain')
    if structured_data.get('nausea'): checked_symptoms.append('nausea')
    if structured_data.get('breathing'): checked_symptoms.append('difficulty breathing')
    if structured_data.get('rash'): checked_symptoms.append('skin rash')
    if structured_data.get('diarrhea'): checked_symptoms.append('diarrhea')
    if structured_data.get('vomiting'): checked_symptoms.append('vomiting')
    
    if checked_symptoms:
        enhanced += ' ' + ' '.join(checked_symptoms)
    
    # Add duration context
    duration = structured_data.get('duration')
    if duration and duration != "Not specified":
        enhanced += f" for {duration}"
    
    # Add severity context
    severity = structured_data.get('severity_level')
    if severity and severity > 5:
        enhanced += f" with {severity}/10 severity"
    
    return enhanced.strip()

# --------------------------------------------------
# Core imports
# --------------------------------------------------
try:
    from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer
    CORE_OK = True
except ImportError as e:
    st.error(f"⚠️ Core module import error: {e}")
    CORE_OK = False

# Advanced features
ADVANCED_FEATURES_OK = False
try:
    from src.multi_disease_detector import MultiDiseaseDetector
    from src.severity_classifier import SeverityClassifier
    from src.personalized_recommender import PersonalizedRecommender, PatientProfile
    from src.feedback_system import FeedbackSystem
    from src.explainability import SymptomMatcher, create_symptom_importance_chart
    ADVANCED_FEATURES_OK = True
except ImportError:
    pass

# Page configuration
st.set_page_config(
    page_title="Cure-Blend - AI Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with animations and better design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated gradient header */
    .main-header {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 700;
        text-align: center;
        padding: 2.5rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        animation: gradientShift 8s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Diagnosis card with glass morphism */
    .diagnosis-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .diagnosis-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
    }
    
    .diagnosis-title {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Confidence badges with glow effect */
    .confidence-badge {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }
    
    .confidence-badge:hover {
        transform: scale(1.05);
    }
    
    .confidence-high { 
        background: linear-gradient(135deg, #00c851 0%, #007E33 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 200, 81, 0.4);
    }
    
    .confidence-medium { 
        background: linear-gradient(135deg, #ffbb33 0%, #ff8800 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(255, 187, 51, 0.4);
    }
    
    .confidence-low { 
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.4);
    }
    
    /* Severity card with pulsing animation */
    .severity-card {
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1.5rem 0;
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .severity-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(0.8); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 0.8; }
    }
    
    .severity-score {
        font-size: 4rem;
        font-weight: 800;
        margin: 1rem 0;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }
    
    .severity-emergency { 
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        animation: emergencyPulse 1s ease-in-out infinite;
    }
    
    @keyframes emergencyPulse {
        0%, 100% { box-shadow: 0 10px 40px rgba(255, 68, 68, 0.6); }
        50% { box-shadow: 0 10px 60px rgba(255, 68, 68, 0.9); }
    }
    
    .severity-severe { background: linear-gradient(135deg, #ff8800 0%, #ff4444 100%); }
    .severity-moderate { background: linear-gradient(135deg, #ffbb33 0%, #ff8800 100%); }
    .severity-mild { background: linear-gradient(135deg, #00c851 0%, #007E33 100%); }
    
    /* Recommendation cards */
    .recommendation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .recommendation-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
    }
    
    .recommendation-title {
        color: #667eea;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Custom progress bar */
    .custom-progress {
        height: 12px;
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .custom-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 1s ease;
    }
    
    /* Stats card */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        margin: 0.5rem 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button improvements */
    .stButton button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 10px;
        font-weight: 600;
        padding: 1rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            padding: 1.5rem 1rem;
        }
        
        .diagnosis-title {
            font-size: 1.5rem;
        }
        
        .severity-score {
            font-size: 3rem;
        }
        
        .stat-number {
            font-size: 2rem;
        }
    }
    
    /* Loading animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Fade in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #00c851 0%, #007E33 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 200, 81, 0.3);
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #ffbb33 0%, #ff8800 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255, 187, 51, 0.3);
    }
    
    /* Error box */
    .error-box {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = None
if 'patient_profile' not in st.session_state:
    st.session_state.patient_profile = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'last_symptoms' not in st.session_state:
    st.session_state.last_symptoms = None
if 'last_enhanced' not in st.session_state:
    st.session_state.last_enhanced = None
if 'structured_data' not in st.session_state:
    st.session_state.structured_data = {}
if 'feedback_system' not in st.session_state:
    if ADVANCED_FEATURES_OK:
        st.session_state.feedback_system = FeedbackSystem()

@st.cache_resource
def load_system():
    """Load the knowledge base (cached)"""
    try:
        if not CORE_OK:
            return None
        kb = load_knowledge_base()
        return kb
    except Exception as e:
        st.error(f"Error loading knowledge base: {e}")
        return None

def create_patient_profile_sidebar():
    """Create patient profile input in sidebar"""
    with st.sidebar:
        st.markdown("### 👤 Patient Profile")
        
        use_profile = st.checkbox("🔒 Enable Personalized Care", value=False,
                                  help="Get personalized recommendations and safety warnings")
        
        if not use_profile:
            return None
        
        with st.expander("📋 Your Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", 0, 120, 30, key="age")
            with col2:
                gender = st.selectbox("Gender", ["male", "female", "other"], key="gender")
            
            st.markdown("**🏥 Special Conditions**")
            col1, col2 = st.columns(2)
            with col1:
                is_pregnant = st.checkbox("Pregnant", key="pregnant")
            with col2:
                is_breastfeeding = st.checkbox("Breastfeeding", key="bf")
            
            st.markdown("**💊 Health Conditions**")
            col1, col2 = st.columns(2)
            with col1:
                has_diabetes = st.checkbox("Diabetes", key="diabetes")
                has_kidney_disease = st.checkbox("Kidney Disease", key="kidney")
            with col2:
                has_hypertension = st.checkbox("Hypertension", key="hyper")
                has_liver_disease = st.checkbox("Liver Disease", key="liver")
        
        profile = PatientProfile(
            age=age, gender=gender, is_pregnant=is_pregnant,
            is_breastfeeding=is_breastfeeding, has_diabetes=has_diabetes,
            has_hypertension=has_hypertension, has_kidney_disease=has_kidney_disease,
            has_liver_disease=has_liver_disease
        )
        
        st.success("✅ Profile Active")
        return profile

def display_diagnosis(disease: str, confidence: float):
    """Display diagnosis with enhanced visuals"""
    if confidence >= 0.7:
        badge_class, level = "confidence-high", "High"
    elif confidence >= 0.4:
        badge_class, level = "confidence-medium", "Medium"
    else:
        badge_class, level = "confidence-low", "Low"
    
    st.markdown(f"""
        <div class="diagnosis-card fade-in">
            <div class="diagnosis-title">
                <span>🎯</span> Diagnosis: {disease}
            </div>
            <div style="margin-top: 1.5rem;">
                <span class="confidence-badge {badge_class}">
                    {level} Confidence • {confidence*100:.1f}%
                </span>
            </div>
            <div class="custom-progress" style="margin-top: 1rem;">
                <div class="custom-progress-bar" style="width: {confidence*100}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_severity(severity):
    """Display severity with visual impact"""
    severity_map = {
        "Emergency": "severity-emergency",
        "Severe": "severity-severe",
        "Moderate": "severity-moderate",
        "Mild": "severity-mild"
    }
    
    card_class = severity_map.get(severity.level, "severity-mild")
    emoji_map = {"Emergency": "🚨", "Severe": "⚠️", "Moderate": "⚡", "Mild": "✓"}
    emoji = emoji_map.get(severity.level, "✓")
    
    st.markdown(f"""
        <div class="severity-card {card_class} fade-in">
            <div>{emoji} Severity Assessment</div>
            <div class="severity-score">{severity.score}<span style="font-size: 2rem;">/100</span></div>
            <div style="font-size: 1.3rem; opacity: 0.9;">{severity.level}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(severity.score / 100)
    
    if severity.level == "Emergency":
        st.markdown("""
            <div class="error-box">
                🚨 <strong>EMERGENCY SITUATION</strong><br/>
                Call emergency services immediately: 911 / 112 / 108<br/>
                Do not wait. Time is critical.
            </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    if severity.recommendations:
        st.markdown("### 💡 Recommended Actions")
        for i, action in enumerate(severity.recommendations, 1):
            st.markdown(f"{i}. {action}")

def display_stats_overview(response: dict, results: dict):
    """Display key statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Confidence</div>
                <div class="stat-number">{response.get('confidence', 0)*100:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        herb_count = len(response.get('herbal_recommendations', []))
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Herbal</div>
                <div class="stat-number">{herb_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        drug_count = len(response.get('drug_recommendations', []))
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Medications</div>
                <div class="stat-number">{drug_count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        severity_score = results.get('severity').score if results.get('severity') else 0
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Severity</div>
                <div class="stat-number">{severity_score}</div>
            </div>
        """, unsafe_allow_html=True)

def display_herbal_recommendations(ingredients: list):
    """Display herbal recommendations with enhanced design"""
    if not ingredients:
        st.info("💡 No herbal recommendations available for this condition.")
        return
    
    st.markdown(f"### 🌿 Herbal Remedies <span style='color: #667eea;'>({len(ingredients)} options)</span>", unsafe_allow_html=True)
    
    for i, ing in enumerate(ingredients, 1):
        name = ing.get('ingredient', 'Unknown')
        score = ing.get('relevance_score', 0)
        benefits = ing.get('benefits', 'General health support')
        active_compounds = ing.get('active_compounds', '')
        usage = ing.get('usage', 'Consult herbalist')
        
        with st.expander(f"**{i}. {name}** ⭐ {score*100:.0f}% Match", expanded=(i <= 2)):
            # Use native Streamlit components for guaranteed rendering
            st.markdown(f"### 🌿 {name}")
            st.markdown(f"**Benefits:** {benefits}")
            if active_compounds:
                st.markdown(f"**Active Compounds:** {active_compounds}")
            st.markdown(f"**Usage:** {usage}")
            st.progress(score, text=f"Relevance: {score*100:.0f}%")

def display_pharmaceutical_recommendations(medications: list, disease: str, do_not_show_antibiotics: bool = False):
    """Display pharmaceutical recommendations with safety highlights"""
    
    def is_antibiotic(med: dict) -> bool:
        """Check if medication is an antibiotic"""
        med_type = med.get('type', '').lower()
        return any(keyword in med_type for keyword in ['antibiotic', 'antibacterial', 'antimicrobial'])
    
    # Filter out antibiotics if confidence too low
    if do_not_show_antibiotics:
        medications = [m for m in medications if not is_antibiotic(m)]
        if not medications:
            st.warning("⚠️ Confidence too low to recommend specific medications. Please consult a healthcare professional.")
            return
        st.warning("⚠️ Due to diagnostic uncertainty, antibiotics are not shown. Only symptomatic relief options displayed.")
    
    if not medications:
        st.info("💡 No pharmaceutical recommendations available.")
        return
    
    st.markdown(f"### 💊 Pharmaceutical Options <span style='color: #667eea;'>({len(medications)} medications)</span>", unsafe_allow_html=True)
    
    if 'dengue' in disease.lower():
        st.markdown("""
            <div class="error-box">
                <strong>🚨 DENGUE SAFETY ALERT</strong><br/>
                ❌ Avoid: Aspirin, Ibuprofen, NSAIDs (bleeding risk)<br/>
                ✅ Safe: Paracetamol only (under medical supervision)<br/>
                🏥 Seek immediate medical care for diagnosis
            </div>
        """, unsafe_allow_html=True)
    
    for i, med in enumerate(medications, 1):
        name = med.get('name', 'Unknown')
        safety = med.get('safety_warning')
        
        with st.expander(f"**{i}. {name.upper()}**{'  🚨' if safety else ''}", expanded=(i <= 2)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Type:** {med.get('type', 'N/A')}")
                st.markdown(f"**Purpose:** {med.get('purpose', 'N/A')}")
                st.markdown(f"**Dosage:** {med.get('dosage', 'As prescribed')}")
                if med.get('brand_names'):
                    st.markdown(f"**Brands:** {', '.join(med['brand_names'])}")
            
            with col2:
                st.markdown(f"**Availability:** {med.get('availability', 'Unknown')}")
                st.markdown(f"**Price Range:** {med.get('price_range', 'Varies')}")
                if med.get('side_effects'):
                    st.warning(f"⚠️ **Side Effects:** {med.get('side_effects')}")
            
            if safety:
                st.error(f"🚨 **SAFETY WARNING:** {safety}")

def analyze_symptoms(symptoms: str, patient_profile: Optional[object], use_ai: bool, use_advanced: bool):
    """Analyze symptoms"""
    if not CORE_OK or st.session_state.knowledge_base is None:
        return {'basic_response': {'error': 'System not initialized'}}
    
    try:
        response = generate_comprehensive_answer(
            symptoms, st.session_state.knowledge_base,
            use_ai=use_ai, include_drugs=True
        )
    except Exception as e:
        return {'basic_response': {'error': str(e)}}
    
    results = {'basic_response': response, 'disease_analysis': None, 'severity': None, 'recommendations': None}
    
    if use_advanced and ADVANCED_FEATURES_OK:
        try:
            detector = MultiDiseaseDetector()
            results['disease_analysis'] = detector.analyze_symptom_overlap(symptoms)
            
            classifier = SeverityClassifier()
            results['severity'] = classifier.analyze_severity(symptoms, response.get('detected_disease', 'Unknown'))
            
            if patient_profile:
                recommender = PersonalizedRecommender()
                results['recommendations'] = recommender.personalize_recommendations(
                    disease=response.get('detected_disease', 'Unknown'),
                    severity_level=results['severity'].level,
                    patient=patient_profile
                )
        except Exception as e:
            st.error("⚠️ Advanced analysis failed")
            st.exception(e)
    
    return results

def main():
    """Main application"""
    if not CORE_OK:
        st.error("⚠️ **System Error**: Core modules not loaded. Run: `pip install -r requirements.txt`")
        st.stop()
    
    # Animated header
    st.markdown('''
        <div class="main-header">
            🏥 Cure-Blend AI
            <div style="font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;">
                Your Intelligent Health Assistant
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings & Status")
        
        # Active features display
        st.markdown("**🔬 Active Features**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("✅ Core AI" if CORE_OK else "❌ Core AI")
            st.markdown("✅ Knowledge Base" if st.session_state.knowledge_base else "⏳ Loading...")
        with col2:
            st.markdown("✅ Advanced" if ADVANCED_FEATURES_OK else "⚠️ Basic Mode")
        
        st.divider()
        
        use_advanced = st.checkbox("🔬 Advanced Analysis", value=ADVANCED_FEATURES_OK,
                                   help="Multi-disease detection & severity scoring", key="adv")
        
        use_ai = st.checkbox("🤖 AI Insights", value=True,
                            help="Detailed AI-powered explanations", key="ai")
        
        # Show what's enabled
        if use_advanced or use_ai:
            st.success(f"{'🔬 ' if use_advanced else ''}{'🤖 ' if use_ai else ''} Enhanced Mode Active")
        
        st.divider()
        
        with st.expander("📊 Detailed System Status"):
            st.markdown(f"**Core System:** {'✅ Active' if CORE_OK else '❌ Error'}")
            st.markdown(f"**Advanced Features:** {'✅ Active' if ADVANCED_FEATURES_OK else '⚠️ Limited'}")
            st.markdown(f"**Knowledge Base:** {'✅ Ready' if st.session_state.knowledge_base else '⏳ Loading'}")
        
        st.divider()
    
    # Patient profile
    patient_profile = create_patient_profile_sidebar() if ADVANCED_FEATURES_OK else None
    
    # Main content
    st.markdown("### 💬 Describe Your Symptoms")
    
    # Initialize defaults to prevent NameError if expander not opened
    fever_check = cough_check = headache_check = fatigue_check = False
    body_pain_check = nausea_check = breathing_check = rash_check = False
    diarrhea_check = vomiting_check = False
    duration = "Not specified"
    severity_level = 5
    
    # Structured symptom checklist for better accuracy
    st.markdown("#### 📋 Quick Symptom Checker *(Optional - Improves Accuracy)*")
    with st.expander("✓ Check your symptoms for better diagnosis", expanded=False):
        st.markdown("**Common Symptoms:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fever_check = st.checkbox("🌡️ Fever", key="fever_check")
            cough_check = st.checkbox("😷 Cough", key="cough_check")
            headache_check = st.checkbox("🤕 Headache", key="headache_check")
            fatigue_check = st.checkbox("😴 Fatigue", key="fatigue_check")
        
        with col2:
            body_pain_check = st.checkbox("💪 Body aches", key="body_pain_check")
            nausea_check = st.checkbox("🤢 Nausea", key="nausea_check")
            breathing_check = st.checkbox("🫁 Breathing issues", key="breathing_check")
            rash_check = st.checkbox("🔴 Rash", key="rash_check")
        
        with col3:
            diarrhea_check = st.checkbox("💩 Diarrhea", key="diarrhea_check")
            vomiting_check = st.checkbox("🤮 Vomiting", key="vomiting_check")
        
        st.markdown("---")
        st.markdown("**Additional Context:**")
        col1, col2 = st.columns(2)
        
        with col1:
            duration = st.selectbox(
                "Duration",
                ["Not specified", "< 1 day", "1-3 days", "3-7 days", "1-2 weeks", "> 2 weeks"],
                key="duration_select"
            )
        
        with col2:
            severity_level = st.slider("Severity (1=mild, 10=severe)", 1, 10, 5, key="severity_slider")
        
        if any([fever_check, cough_check, headache_check, fatigue_check, body_pain_check, 
                nausea_check, breathing_check, rash_check, diarrhea_check, vomiting_check]):
            st.success("✅ Structured data captured - this will improve diagnosis accuracy!")
    
    # Collect structured data
    structured_data = {
        'fever': fever_check,
        'cough': cough_check,
        'headache': headache_check,
        'fatigue': fatigue_check,
        'body_pain': body_pain_check,
        'nausea': nausea_check,
        'breathing': breathing_check,
        'rash': rash_check,
        'diarrhea': diarrhea_check,
        'vomiting': vomiting_check,
        'duration': duration,
        'severity_level': severity_level
    }
    
    # Quick examples with better styling
    st.markdown("**Quick Examples:**")
    col1, col2, col3, col4 = st.columns(4)
    examples = [
        ("🤒 Flu", "fever headache body aches fatigue cough"),
        ("🤕 Migraine", "severe headache sensitivity to light nausea"),
        ("😷 Cold", "runny nose sneezing sore throat cough"),
        ("🦠 UTI", "frequent urination burning sensation lower abdominal pain")
    ]
    
    example_clicked = None
    for i, (col, (label, text)) in enumerate(zip([col1, col2, col3, col4], examples)):
        with col:
            if st.button(label, key=f"ex{i}", use_container_width=True):
                example_clicked = text
    
    symptoms = st.text_area(
        "Your Symptoms",
        value=example_clicked if example_clicked else "",
        height=120,
        placeholder="Example: frequent urination, burning sensation, lower abdominal discomfort...",
        help="💡 Be specific: include duration, intensity, and exact location",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        analyze_button = st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🔄 Clear Results", use_container_width=True)
    
    if clear_button:
        st.session_state.analysis_results = None
        st.rerun()
    
    # Load knowledge base
    if st.session_state.knowledge_base is None:
        with st.spinner("📚 Loading medical knowledge base..."):
            st.session_state.knowledge_base = load_system()
        if st.session_state.knowledge_base:
            st.markdown('<div class="success-message">✅ System Ready - Knowledge Base Loaded</div>', unsafe_allow_html=True)
    
    # Analyze
    if analyze_button:
        if not symptoms.strip():
            st.error("⚠️ Please enter your symptoms first")
        else:
            # Enhance symptoms with structured data
            enhanced_symptoms = enhance_symptoms_with_context(symptoms, structured_data)
            
            # Show what was processed
            if enhanced_symptoms != normalize_symptoms(symptoms):
                with st.expander("🔍 Enhanced Symptom Analysis"):
                    st.success("✅ Your input was enhanced with structured data for better accuracy!")
                    st.markdown(f"**Original:** {symptoms}")
                    st.markdown(f"**Enhanced:** {enhanced_symptoms}")
            
            with st.spinner("🔍 Analyzing your symptoms..."):
                results = analyze_symptoms(enhanced_symptoms, patient_profile, use_ai, use_advanced)
                st.session_state.analysis_results = results
                st.session_state.last_symptoms = symptoms
                st.session_state.last_enhanced = enhanced_symptoms
                st.session_state.structured_data = structured_data  # Save for calibration
            st.markdown('<div class="success-message">✅ Analysis Complete!</div>', unsafe_allow_html=True)
    
    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        response = results['basic_response']
        
        if 'error' in response:
            st.error(f"⚠️ {response['error']}")
            return
        
        st.divider()
        st.markdown("## 📋 Analysis Results")
        
        disease = response.get('detected_disease', 'Unknown')
        raw_confidence = response.get('confidence', 0.5)
        
        # Apply confidence calibration
        symptoms_used = st.session_state.get('last_enhanced', st.session_state.get('last_symptoms', ''))
        structured = st.session_state.get('structured_data', {})
        confidence = calibrate_confidence(raw_confidence, symptoms_used, disease, structured)
        
        # Show confidence improvement if significant
        if abs(confidence - raw_confidence) >= 0.05:
            with st.expander("📊 Confidence Calibration Applied"):
                st.markdown(f"**Model Confidence:** {raw_confidence*100:.1f}%")
                st.markdown(f"**Calibrated Confidence:** {confidence*100:.1f}%")
                improvement = (confidence - raw_confidence) * 100
                if improvement > 0:
                    st.success(f"✅ Confidence improved by {improvement:.1f}% based on symptom quality and diagnostic markers!")
                else:
                    st.info(f"⚠️ Confidence adjusted down by {abs(improvement):.1f}% due to vague symptom description.")
        
        # IMPORTANT: Override diagnosis early if confidence too low
        # This ensures all downstream logic (stats, severity) uses correct disease state
        do_not_show_antibiotics = False
        if confidence < 0.4:
            do_not_show_antibiotics = True
            disease = "Uncertain – Multiple systems involved"
        
        # Low confidence - offer to improve with more info
        if confidence < 0.6 and 'follow_up_done' not in st.session_state:
            st.markdown("""
                <div class="warning-box">
                    <strong>💡 Confidence can be improved!</strong><br/>
                    Answer a few quick questions to increase diagnostic accuracy.
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📋 Answer these to improve diagnosis", expanded=True):
                st.markdown("**Additional Questions:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    recent_travel = st.selectbox("Recent travel?", ["No", "Yes - domestic", "Yes - international"])
                    sick_contact = st.selectbox("Contact with sick people?", ["No", "Yes", "Unsure"])
                    chronic_conditions = st.multiselect("Existing conditions?", 
                        ["None", "Diabetes", "Hypertension", "Asthma", "Heart disease", "Other"])
                
                with col2:
                    fever_pattern = st.selectbox("Fever pattern (if applicable)?", 
                        ["No fever", "Continuous", "Comes and goes", "Only at night"])
                    symptom_onset = st.selectbox("How did symptoms start?", 
                        ["Suddenly (within hours)", "Gradually (over days)", "Unsure"])
                
                additional_info = st.text_input("Any other important details?")
                
                if st.button("🔄 Re-analyze with Additional Info", type="secondary"):
                    # Reconstruct enhanced symptoms with new info
                    extra_context = []
                    if recent_travel != "No":
                        extra_context.append(f"recent {recent_travel.lower()}")
                    if sick_contact == "Yes":
                        extra_context.append("exposure to sick contacts")
                    if fever_pattern != "No fever":
                        extra_context.append(f"{fever_pattern.lower()} fever pattern")
                    if additional_info:
                        extra_context.append(additional_info)
                    
                    if extra_context:
                        improved_symptoms = st.session_state.last_enhanced + " " + " ".join(extra_context)
                        
                        with st.spinner("🔍 Re-analyzing with additional context..."):
                            results = analyze_symptoms(improved_symptoms, patient_profile, use_ai, use_advanced)
                            st.session_state.analysis_results = results
                            st.session_state.follow_up_done = True
                        
                        st.success("✅ Analysis updated with additional information!")
                        st.rerun()
        
        # Stats overview
        if use_advanced:
            display_stats_overview(response, results)
            st.markdown("<br/>", unsafe_allow_html=True)
        
        # Diagnosis
        display_diagnosis(disease, confidence)
        
        # Severity
        if use_advanced and results.get('severity'):
            st.markdown("### 🔬 Severity Assessment")
            display_severity(results['severity'])
        
        # Multi-disease analysis
        if use_advanced and results.get('disease_analysis'):
            analysis = results['disease_analysis']
            if analysis.get('has_multiple_conditions'):
                st.markdown("""
                    <div class="warning-box">
                        <strong>⚠️ Multiple Conditions Possible</strong><br/>
                        Our analysis suggests you may have overlapping symptoms.
                    </div>
                """, unsafe_allow_html=True)
                for combo in analysis['comorbidities'][:3]:
                    st.write(f"• **{combo['disease']}**: {combo['confidence']*100:.1f}% confidence")
        
        # Personalized warnings
        if results.get('recommendations') and patient_profile:
            warnings = results['recommendations'].get('warnings', [])
            if warnings:
                st.markdown("""
                    <div class="error-box">
                        <strong>🚨 PERSONALIZED SAFETY WARNINGS</strong>
                    </div>
                """, unsafe_allow_html=True)
                for warning in warnings:
                    st.write(f"• {warning}")
        
        # Recommendations
        st.divider()
        st.markdown("## 💊 Treatment Recommendations")
        
        tab1, tab2, tab3 = st.tabs(["🌿 Herbal Remedies", "💊 Pharmaceutical", "🤖 AI Insights"])
        
        with tab1:
            display_herbal_recommendations(response.get('herbal_recommendations', []))
        
        with tab2:
            display_pharmaceutical_recommendations(response.get('drug_recommendations', []), disease, do_not_show_antibiotics)
        
        with tab3:
            ai_insights = response.get('ai_insights', 'AI insights not available.')
            st.markdown(ai_insights, unsafe_allow_html=False)
        
        # Low confidence warning
        if confidence < 0.5:
            st.markdown(f"""
                <div class="warning-box">
                    <strong>⚠️ LOW CONFIDENCE ALERT ({confidence*100:.1f}%)</strong><br/>
                    The system is uncertain. Possible reasons: Vague symptoms • Multiple conditions • Rare condition<br/>
                    <strong>👨‍⚕️ STRONGLY RECOMMEND: Consult a healthcare professional</strong>
                </div>
            """, unsafe_allow_html=True)
        
        # Medical disclaimer (collapsible)
        st.divider()
        with st.expander("⚠️ Medical Disclaimer - Important"):
            st.warning("""
**This is an AI-powered informational tool ONLY.**

• Always consult qualified healthcare professionals
• Do not use for emergency situations  
• Not a substitute for professional medical advice
• Individual results may vary
            """)
    
    # Footer
    st.divider()
    with st.expander("ℹ️ About Cure-Blend"):
        st.markdown("""
        ### 🏥 AI-Powered Health Recommendation System
        
        **Features:** 🔍 Disease Detection • 📊 Severity Assessment • 🌿 Herbal Remedies • 💊 Pharmaceuticals • 🤖 AI Insights
        
        **Copyright © 2026 vishwaksen21 - All Rights Reserved**
        
        Proprietary Software - Unauthorized use prohibited
        """)

if __name__ == "__main__":
    main()
