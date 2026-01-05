"""
Cure-Blend: AI-Powered Health Recommendation System
Improved Streamlit Web Application

Copyright (c) 2026 vishwaksen21
All Rights Reserved - Proprietary Software
"""

import streamlit as st
import sys
import os
import json
from typing import Optional, Dict, List
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Core imports with error handling
try:
    from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer
    CORE_OK = True
except ImportError as e:
    st.error(f"⚠️ Core module import error: {e}")
    CORE_OK = False

# Try to import advanced features
ADVANCED_FEATURES_OK = False
try:
    from src.multi_disease_detector import MultiDiseaseDetector, format_multi_disease_output
    from src.severity_classifier import SeverityClassifier, format_severity_output
    from src.personalized_recommender import (
        PersonalizedRecommender,
        PatientProfile,
        AgeGroup,
        format_personalized_output
    )
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

# Enhanced CSS
st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        font-size: clamp(1.8rem, 5vw, 3rem);
        color: #1f77b4;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .diagnosis-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .confidence-high { background: #00c851; color: white; }
    .confidence-medium { background: #ffbb33; color: black; }
    .confidence-low { background: #ff4444; color: white; }
    
    .severity-card {
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .severity-emergency { background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%); }
    .severity-severe { background: linear-gradient(135deg, #ff8800 0%, #ff4444 100%); }
    .severity-moderate { background: linear-gradient(135deg, #ffbb33 0%, #ff8800 100%); }
    .severity-mild { background: linear-gradient(135deg, #00c851 0%, #007E33 100%); }
    
    .recommendation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .recommendation-card h4 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stButton button {
            width: 100%;
            font-size: 1.1rem;
            padding: 0.75rem;
        }
        .main-header {
            font-size: 1.5rem;
        }
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
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
if 'feedback_system' not in st.session_state:
    if ADVANCED_FEATURES_OK:
        st.session_state.feedback_system = FeedbackSystem()
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False

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
        st.header("👤 Patient Profile")
        
        use_profile = st.checkbox("Enable Personalized Recommendations", value=False,
                                  help="Get personalized safety warnings based on your profile")
        
        if not use_profile:
            return None
        
        with st.expander("📋 Enter Information", expanded=True):
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["male", "female", "other"])
            
            st.subheader("Special Conditions")
            is_pregnant = st.checkbox("Pregnant")
            is_breastfeeding = st.checkbox("Breastfeeding")
            
            st.subheader("Health Conditions")
            has_diabetes = st.checkbox("Diabetes")
            has_hypertension = st.checkbox("Hypertension")
            has_kidney_disease = st.checkbox("Kidney Disease")
            has_liver_disease = st.checkbox("Liver Disease")
        
        profile = PatientProfile(
            age=age,
            gender=gender,
            is_pregnant=is_pregnant,
            is_breastfeeding=is_breastfeeding,
            has_diabetes=has_diabetes,
            has_hypertension=has_hypertension,
            has_kidney_disease=has_kidney_disease,
            has_liver_disease=has_liver_disease
        )
        
        st.success("✅ Profile Created")
        return profile

def display_diagnosis(disease: str, confidence: float):
    """Display diagnosis in a card"""
    # Confidence badge
    if confidence >= 0.7:
        badge_class = "confidence-high"
        level = "High"
    elif confidence >= 0.4:
        badge_class = "confidence-medium"
        level = "Medium"
    else:
        badge_class = "confidence-low"
        level = "Low"
    
    st.markdown(f"""
        <div class="diagnosis-card">
            <h2 style="margin: 0; color: #667eea;">🎯 Diagnosis: {disease}</h2>
            <div style="margin-top: 1rem;">
                <span class="confidence-badge {badge_class}">
                    Confidence: {level} ({confidence*100:.1f}%)
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_severity(severity):
    """Display severity assessment"""
    severity_map = {
        "Emergency": "severity-emergency",
        "Severe": "severity-severe",
        "Moderate": "severity-moderate",
        "Mild": "severity-mild"
    }
    
    card_class = severity_map.get(severity.level, "severity-mild")
    
    st.markdown(f"""
        <div class="severity-card {card_class}">
            <div>🚨 Severity: {severity.level}</div>
            <div style="font-size: 3rem; margin: 1rem 0;">{severity.score}/100</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(severity.score / 100)
    
    if severity.level == "Emergency":
        st.error("🚨 **EMERGENCY: CALL AMBULANCE IMMEDIATELY (911/112/108)**")
        st.error("Do not wait. Time is critical.")
    
    if severity.recommendations:
        st.subheader("💡 Recommended Actions")
        for action in severity.recommendations:
            st.write(f"• {action}")

def display_herbal_recommendations(ingredients: list):
    """Display herbal recommendations"""
    if not ingredients:
        st.info("No herbal recommendations available for this condition.")
        return
    
    st.subheader(f"🌿 Herbal Remedies ({len(ingredients)} recommendations)")
    
    for i, ing in enumerate(ingredients, 1):
        name = ing.get('ingredient', 'Unknown')
        score = ing.get('relevance_score', 0)
        
        with st.expander(f"**{i}. {name}**", expanded=(i <= 2)):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Benefits:** {ing.get('benefits', 'General health support')}")
                if ing.get('active_compounds'):
                    st.markdown(f"**Active Compounds:** {ing.get('active_compounds')}")
                st.markdown(f"**Usage:** {ing.get('usage', 'Consult herbalist')}")
            
            with col2:
                st.metric("Relevance", f"{score*100:.0f}%")
                st.progress(score)

def display_pharmaceutical_recommendations(medications: list, disease: str):
    """Display pharmaceutical recommendations"""
    if not medications:
        st.info("No pharmaceutical recommendations available for this condition.")
        return
    
    st.subheader(f"💊 Pharmaceutical Options ({len(medications)} medications)")
    
    # Dengue safety warning
    if 'dengue' in disease.lower():
        st.error("""
        🚨 **DENGUE SAFETY WARNING**
        - ❌ Avoid Aspirin and NSAIDs (Ibuprofen, Diclofenac) - bleeding risk
        - ✅ Use Paracetamol ONLY under medical supervision
        - 🏥 Seek immediate medical care for diagnosis
        """)
    
    for i, med in enumerate(medications, 1):
        name = med.get('name', 'Unknown')
        
        with st.expander(f"**{i}. {name.upper()}**", expanded=(i <= 2)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Type:** {med.get('type', 'N/A')}")
                st.markdown(f"**Purpose:** {med.get('purpose', 'N/A')}")
                st.markdown(f"**Dosage:** {med.get('dosage', 'As prescribed')}")
                
                if med.get('brand_names'):
                    brands = ", ".join(med['brand_names'])
                    st.markdown(f"**Brands:** {brands}")
            
            with col2:
                st.markdown(f"**Availability:** {med.get('availability', 'Unknown')}")
                st.markdown(f"**Price:** {med.get('price_range', 'Varies')}")
                
                if med.get('side_effects'):
                    st.warning(f"⚠️ **Side Effects:** {med.get('side_effects')}")
                
                if med.get('safety_warning'):
                    st.error(f"🚨 {med.get('safety_warning')}")

def analyze_symptoms(symptoms: str, patient_profile: Optional[PatientProfile], use_ai: bool, use_advanced: bool):
    """Analyze symptoms with all features"""
    if not CORE_OK or st.session_state.knowledge_base is None:
        return {'basic_response': {'error': 'System not initialized'}}
    
    knowledge = st.session_state.knowledge_base
    
    try:
        response = generate_comprehensive_answer(
            symptoms,
            knowledge,
            use_ai=use_ai,
            include_drugs=True
        )
    except Exception as e:
        st.error(f"Analysis error: {e}")
        response = {
            'detected_disease': 'Error',
            'confidence': 0.0,
            'herbal_recommendations': [],
            'drug_recommendations': [],
            'ai_insights': f'Error: {str(e)}'
        }
    
    results = {
        'basic_response': response,
        'disease_analysis': None,
        'severity': None,
        'recommendations': None
    }
    
    if use_advanced and ADVANCED_FEATURES_OK:
        try:
            detector = MultiDiseaseDetector()
            results['disease_analysis'] = detector.analyze_symptom_overlap(symptoms)
            
            classifier = SeverityClassifier()
            primary_disease = response.get('detected_disease', 'Unknown')
            results['severity'] = classifier.analyze_severity(symptoms, primary_disease)
            
            if patient_profile:
                recommender = PersonalizedRecommender()
                results['recommendations'] = recommender.personalize_recommendations(
                    disease=primary_disease,
                    severity_level=results['severity'].level,
                    patient=patient_profile
                )
        except Exception as e:
            st.warning(f"Advanced features error: {e}")
    
    return results

def main():
    """Main application"""
    if not CORE_OK:
        st.error("⚠️ **System Error**: Core modules not loaded")
        st.info("Run: `pip install -r requirements.txt`")
        st.stop()
    
    # Header
    st.markdown('''
        <div class="main-header">
            🏥 Cure-Blend AI Health Assistant 🌿
        </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        
        with st.expander("📊 System Status"):
            st.write(f"**Core:** {'✅' if CORE_OK else '❌'}")
            st.write(f"**Advanced:** {'✅' if ADVANCED_FEATURES_OK else '⚠️'}")
            st.write(f"**Knowledge Base:** {'✅' if st.session_state.knowledge_base else '⚠️'}")
        
        use_advanced = st.checkbox("Advanced Analysis", value=ADVANCED_FEATURES_OK,
                                   help="Multi-disease detection & severity scoring")
        
        use_ai = st.checkbox("AI Insights", value=True,
                            help="Detailed AI explanations")
        
        st.divider()
    
    # Patient profile
    patient_profile = create_patient_profile_sidebar() if ADVANCED_FEATURES_OK else None
    
    # Main content
    st.header("💬 Describe Your Symptoms")
    
    # Quick examples
    col1, col2, col3, col4 = st.columns(4)
    examples = {
        "🤒 Flu": "fever headache body aches fatigue cough",
        "🤕 Migraine": "severe headache sensitivity to light nausea",
        "😷 Cold": "runny nose sneezing sore throat cough",
        "🦠 UTI": "frequent urination burning sensation lower abdominal pain"
    }
    
    example_clicked = None
    for i, (col, (label, text)) in enumerate(zip([col1, col2, col3, col4], examples.items())):
        with col:
            if st.button(label, key=f"ex{i}", use_container_width=True):
                example_clicked = text
    
    symptoms = st.text_area(
        "Enter your symptoms:",
        value=example_clicked if example_clicked else "",
        height=120,
        placeholder="Example: frequent urination, burning sensation, lower abdominal discomfort",
        help="Be specific: include duration, intensity, and location"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_button = st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🔄 Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.analysis_results = None
        st.rerun()
    
    # Load knowledge base
    if st.session_state.knowledge_base is None:
        with st.spinner("📚 Loading medical knowledge..."):
            st.session_state.knowledge_base = load_system()
        if st.session_state.knowledge_base:
            st.success("✅ System ready!")
    
    # Analyze
    if analyze_button:
        if not symptoms.strip():
            st.error("⚠️ Please enter symptoms first")
        else:
            with st.spinner("🔍 Analyzing symptoms..."):
                results = analyze_symptoms(symptoms, patient_profile, use_ai, use_advanced)
                st.session_state.analysis_results = results
                st.session_state.last_symptoms = symptoms
            st.success("✅ Analysis complete!")
    
    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        response = results['basic_response']
        
        if 'error' in response:
            st.error(f"⚠️ {response['error']}")
            return
        
        st.divider()
        st.header("📋 Analysis Results")
        
        disease = response.get('detected_disease', 'Unknown')
        confidence = response.get('confidence', 0.5)
        
        # Display diagnosis
        display_diagnosis(disease, confidence)
        
        # Severity analysis
        if use_advanced and results.get('severity'):
            st.header("🔬 Severity Assessment")
            display_severity(results['severity'])
            st.divider()
        
        # Multi-disease analysis
        if use_advanced and results.get('disease_analysis'):
            disease_analysis = results['disease_analysis']
            if disease_analysis.get('has_multiple_conditions'):
                st.warning("⚠️ **Possible Multiple Conditions Detected**")
                for comorbidity in disease_analysis['comorbidities']:
                    st.write(f"• **{comorbidity['disease']}**: {comorbidity['confidence']*100:.1f}%")
                st.divider()
        
        # Personalized warnings
        if results.get('recommendations') and patient_profile:
            warnings = results['recommendations'].get('warnings', [])
            if warnings:
                st.error("⚠️ **PERSONALIZED WARNINGS**")
                for warning in warnings:
                    st.write(f"• {warning}")
                st.divider()
        
        # Recommendations
        st.header("💊 Treatment Recommendations")
        
        tab1, tab2, tab3 = st.tabs(["🌿 Herbal", "💊 Pharmaceutical", "🤖 AI Insights"])
        
        with tab1:
            display_herbal_recommendations(response.get('herbal_recommendations', []))
        
        with tab2:
            display_pharmaceutical_recommendations(response.get('drug_recommendations', []), disease)
        
        with tab3:
            ai_insights = response.get('ai_insights', 'No AI insights available.')
            st.markdown(ai_insights)
        
        # Low confidence warning
        if confidence < 0.5:
            st.warning(f"""
            ⚠️ **LOW CONFIDENCE ({confidence*100:.1f}%)**
            
            The system is uncertain about this diagnosis. This could mean:
            - Symptoms are vague or incomplete
            - Multiple conditions are possible
            - Rare or complex condition
            
            **RECOMMENDATION**: Consult a healthcare professional.
            """)
        
        # Disclaimer
        st.divider()
        st.error("""
        ⚠️ **MEDICAL DISCLAIMER**
        
        This is an AI-powered informational tool ONLY. Always consult a qualified healthcare
        professional for diagnosis and treatment. Do not use for emergencies.
        """)
    
    # Footer
    st.divider()
    with st.expander("ℹ️ About Cure-Blend"):
        st.markdown("""
        ### AI-Powered Health Recommendation System
        
        **Features:**
        - 🔍 Multi-disease detection
        - 📊 Severity assessment
        - 🌿 Herbal remedies
        - 💊 Pharmaceutical options
        - 🤖 AI insights
        
        **Copyright © 2026 vishwaksen21 - All Rights Reserved**
        """)

if __name__ == "__main__":
    main()
