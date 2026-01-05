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
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Core imports
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
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Cure-Blend AI Health Assistant v3.0"
    }
)

# Clean and simple CSS - minimal styling for maximum compatibility
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
}
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg,#667eea,#764ba2);
    color: white;
    border-radius: 16px;
}
.card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    margin-top: 1rem;
}
.warning {
    background: #ff8800;
    color: white;
    padding: 1rem;
    border-radius: 10px;
}
.error {
    background: #cc0000;
    color: white;
    padding: 1rem;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None

if "results" not in st.session_state:
    st.session_state.results = None

# --------------------------------------------------
# Load KB
# --------------------------------------------------
@st.cache_resource
def load_kb():
    return load_knowledge_base()

# --------------------------------------------------
# UI helpers
# --------------------------------------------------
def display_diagnosis(disease: str, confidence: float):
    st.markdown("### 🎯 Diagnosis")
    st.markdown(f"**{disease}**")
    st.progress(confidence)
    st.metric("Confidence", f"{confidence*100:.1f}%")

def display_disclaimer():
    st.error("""
⚠️ **MEDICAL DISCLAIMER**

This tool is for informational purposes only.
Always consult a certified medical professional.
Do NOT use for emergencies.
""")
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
        level, color = "High", "🟢"
    elif confidence >= 0.4:
        level, color = "Medium", "🟡"
    else:
        level, color = "Low", "🔴"
    
    # Use container for better layout
    with st.container():
        st.markdown("### 🎯 Diagnosis")
        st.markdown(f"## {disease}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.progress(confidence)
        with col2:
            st.metric("Confidence", f"{confidence*100:.1f}%", delta=f"{color} {level}")

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
    
    # Determine color based on severity
    if severity.level == "Emergency":
        color = "red"
    elif severity.level == "Severe":
        color = "orange"
    elif severity.level == "Moderate":
        color = "yellow"
    else:
        color = "green"
    
    st.markdown(f"### {emoji} Severity Assessment: {severity.level}")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Score", f"{severity.score}/100")
    with col2:
        st.progress(severity.score / 100)
    
    if severity.level == "Emergency":
        st.error("""
        🚨 **EMERGENCY SITUATION**
        
        Call emergency services immediately: 911 / 112 / 108
        
        Do not wait. Time is critical.
        """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            etric("Confidence", f"{response.get('confidence', 0)*100:.0f}%")
    
    with col2:
        herb_count = len(response.get('herbal_recommendations', []))
        st.metric("Herbal Remedies", herb_count)
    
    with col3:
        drug_count = len(response.get('drug_recommendations', []))
        st.metric("Medications", drug_count)
    
    with col4:
        severity_score = results.get('severity').score if results.get('severity') else 0
        st.metric("Severity Score", severity_scor
def display_herbal_recommendations(ingredients: list):
    """Display herbal recommendations with enhanced design"""
    if not ingredients:
        st.info("💡 No herbal recommendations available for this condition.")
        return
    
    st.markdown(f"### 🌿 Herbal Remedies ({len(ingredients)} options)")
    
    for i, ing in enumerate(ingredients, 1):
        name = ing.get('ingredient', 'Unknown')
        score = ing.get('relevance_score', 0)
        
        with st.expander(f"**{i}. {name}** ⭐ {score*100:.0f}% Match", expanded=(i <= 2)):
            st.markdown(f"#### 🌿 {name}")
            st.markdown(f"**Benefits:** {ing.get('benefits', 'General health support')}")
            
            if ing.get('active_compounds'):
                st.markdown(f"**Active Compounds:** {ing.get('active_compounds')}")
            
            st.markdown(f"**Usage:** {ing.get('usage', 'Consult herbalist')}")
            
            # Show relevance as progress bar
            st.progress(score)
            st.caption(f"Relevance: {score*100:.0f}%")

def display_pharmaceutical_recommendations(medications: list, disease: str):
    """Display pharmaceutical recommendations with safety highlights"""
    if not medications:
        st.info("💡 No pharmaceutical recommendations available.")
        return
    
    st.markdown(f"### 💊 Pharmaceutical Options ({len(medications)} medications)")
    
    if 'dengue' in disease.lower():
        st.error("""
        🚨 **DENGUE SAFETY ALERT**
        
        ❌ Avoid: Aspirin, Ibuprofen, NSAIDs (bleeding risk)
        
        ✅ Safe: Paracetamol only (under medical supervision)
        
        🏥 Seek immediate medical care for diagnosis
        """)
    
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

def analyze_symptoms(symptoms: str, patient_profile: Optional[PatientProfile], use_ai: bool, use_advanced: bool):
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
        except Exception:
            pass
    
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
        st.markdown("### ⚙️ Settings")
        
        with st.expander("📊 System Status", expanded=False):
            st.markdown(f"**Core System:** {'✅ Active' if CORE_OK else '❌ Error'}")
            st.markdown(f"**Advanced Features:** {'✅ Active' if ADVANCED_FEATURES_OK else '⚠️ Limited'}")
            st.markdown(f"**Knowledge Base:** {'✅ Ready' if st.session_state.knowledge_base else '⏳ Loading'}")
        
        use_advanced = st.checkbox("🔬 Advanced Analysis", value=ADVANCED_FEATURES_OK,
                                   help="Multi-disease detection & severity scoring", key="adv")
      Header
    st.title("🏥 Cure-Blend AI")
    st.subheader("Your Intelligent Health Assistant")
    st.markdown("---"
    # Main content
    st.markdown("### 💬 Describe Your Symptoms")
    
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
            with st.spinner("🔍 Analyzing your symptoms..."):
                results = analyze_symptoms(symptoms, patient_profile, use_ai, use_advanced)
                st.session_state.analysis_results = results
                st.session_state.last_symptoms = symptoms
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
        
        diseasesuccess("✅ System Ready - Knowledge Base Loaded"
        confidence = response.get('confidence', 0.5)
        
        # Stats overview
        if use_advanced:
            display_stats_overview(response, results)
            st.markdown("<br/>", unsafe_allow_html=True)
        
        # Diagnosis
        display_diagnosis(disease, confidence)
        
        # Seversuccess("✅ Analysis Complete!"
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
                """warning("""
                ⚠️ **Multiple Conditions Possible**
                
                Our analysis suggests you may have overlapping symptoms.
                """nd patient_profile:
            warnings = results['recommendations'].get('warnings', [])
            if warnings:
                st.markdown("""
                    <div class="error-box">
                        <strong>🚨 PERSONALIZED SAFETY WARNINGS</strong>
                    </div>
                """, unsafe_allow_html=True)
                for warning in warnings:
                   error("🚨 **PERSONALIZED SAFETY WARNINGS**"endations")
        
        tab1, tab2, tab3 = st.tabs(["🌿 Herbal Remedies", "💊 Pharmaceutical", "🤖 AI Insights"])
        
        with tab1:
            display_herbal_recommendations(response.get('herbal_recommendations', []))
        
        with tab2:
            display_pharmaceutical_recommendations(response.get('drug_recommendations', []), disease)
        
        with tab3:
            ai_insights = response.get('ai_insights', 'AI insights not available.')
            st.markdown(ai_insights)
        
        # Low confidence warning
        if confidence < 0.5:
            st.markdown(f"""
                <div class="warning-box">
                    <strong>⚠️ LOW CONFIDENCE ALERT ({confidence*100:.1f}%)</strong><br/><br/>
                    The system is uncertain about this diagnosis. Possible reasons:<br/>
                    • Symptoms are vague or incomplete<br/>
               warning(f"""
            ⚠️ **LOW CONFIDENCE ALERT ({confidence*100:.1f}%)**
            
            The system is uncertain about this diagnosis. Possible reasons:
            - Symptoms are vague or incomplete
            - Multiple conditions match your description
            - Rare or complex condition
            
            👨‍⚕️ **RECOMMENDATION: Consult a healthcare professional**
            """
                <strong>⚠️ MEDICAL DISCLAIMER</strong><br/><br/>
                This is an AI-powered informational tool ONLY.<br/>
                • Always consult qualified healthcare professionals<br/>
           error("""
        ⚠️ **MEDICAL DISCLAIMER**
        
        This is an AI-powered informational tool ONLY.
        - Always consult qualified healthcare professionals
        - Do not use for emergency situations
        - Not a substitute for professional medical advice
        - Individual results may vary
        """
        ### 🏥 AI-Powered Health Recommendation System
        
        **Features:** 🔍 Disease Detection • 📊 Severity Assessment • 🌿 Herbal Remedies • 💊 Pharmaceuticals • 🤖 AI Insights
        
        **Copyright © 2026 vishwaksen21 - All Rights Reserved**
        
        Proprietary Software - Unauthorized use prohibited
        """)

if __name__ == "__main__":
    main()
