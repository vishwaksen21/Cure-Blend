"""
Advanced Features Demo - Interactive CLI

Demonstrates all Priority 4 advanced features:
1. Multi-disease detection
2. Severity scoring
3. Personalized recommendations
"""

import sys
sys.path.append('/workspaces/Cure-Blend')

from src.multi_disease_detector import MultiDiseaseDetector, format_multi_disease_output
from src.severity_classifier import SeverityClassifier, format_severity_output
from src.personalized_recommender import (
    PersonalizedRecommender, 
    PatientProfile,
    AgeGroup,
    format_personalized_output
)

class AdvancedHealthAssistant:
    """Integrated advanced health assistant"""
    
    def __init__(self):
        print("🔧 Loading advanced health assistant...")
        self.detector = MultiDiseaseDetector()
        self.severity_classifier = SeverityClassifier()
        self.recommender = PersonalizedRecommender()
        print("✅ All systems loaded!")
    
    def analyze_patient(self, symptoms: str, patient: PatientProfile = None):
        """Complete patient analysis with all advanced features"""
        
        if patient is None:
            patient = PatientProfile(age=35)  # Default adult patient
        
        print("\n" + "="*70)
        print("COMPREHENSIVE PATIENT ANALYSIS")
        print("="*70)
        
        # Step 1: Multi-disease detection
        print("\n🔍 STEP 1: ANALYZING SYMPTOMS...")
        disease_analysis = self.detector.analyze_symptom_overlap(symptoms)
        primary_disease = disease_analysis['primary_disease']['disease']
        primary_confidence = disease_analysis['primary_disease']['confidence']
        
        print(f"\n✅ Analysis complete!")
        print(f"   Primary: {primary_disease} ({primary_confidence*100:.1f}% confidence)")
        if disease_analysis['has_multiple_conditions']:
            print(f"   ⚠️ Possible comorbidities detected!")
        
        # Step 2: Severity assessment
        print("\n🔍 STEP 2: ASSESSING SEVERITY...")
        severity = self.severity_classifier.analyze_severity(symptoms, primary_disease)
        print(f"\n✅ Severity assessed!")
        print(f"   Level: {severity.level}")
        print(f"   Score: {severity.score}/100")
        print(f"   Urgent: {'Yes' if severity.urgent else 'No'}")
        
        # Step 3: Personalized recommendations
        print("\n🔍 STEP 3: GENERATING PERSONALIZED RECOMMENDATIONS...")
        recommendations = self.recommender.personalize_recommendations(
            disease=primary_disease,
            severity_level=severity.level,
            patient=patient
        )
        print(f"\n✅ Recommendations generated!")
        print(f"   Warnings: {len(recommendations['warnings'])}")
        print(f"   Contraindications: {len(recommendations['contraindications'])}")
        print(f"   Special considerations: {len(recommendations['dose_adjustments'])}")
        
        # Display results
        print("\n" + "="*70)
        print("DETAILED RESULTS")
        print("="*70)
        
        print(format_multi_disease_output(disease_analysis))
        print(format_severity_output(severity))
        print(format_personalized_output(recommendations))
        
        return {
            'disease_analysis': disease_analysis,
            'severity': severity,
            'recommendations': recommendations
        }


def interactive_demo():
    """Interactive demonstration"""
    assistant = AdvancedHealthAssistant()
    
    print("\n" + "="*70)
    print("ADVANCED FEATURES DEMO")
    print("="*70)
    print("\nThis demo showcases Priority 4 advanced features:")
    print("  • Multi-disease detection")
    print("  • Symptom severity scoring")
    print("  • Personalized recommendations")
    
    # Demo scenarios
    scenarios = [
        {
            'name': "Scenario 1: Elderly patient with respiratory symptoms",
            'symptoms': "severe difficulty breathing with chest tightness persistent cough",
            'patient': PatientProfile(age=72, has_diabetes=True)
        },
        {
            'name': "Scenario 2: Pregnant woman with infection symptoms",
            'symptoms': "frequent urination burning sensation lower abdominal discomfort",
            'patient': PatientProfile(age=28, is_pregnant=True)
        },
        {
            'name': "Scenario 3: Child with fever",
            'symptoms': "high fever headache body aches sore throat",
            'patient': PatientProfile(age=8)
        },
        {
            'name': "Scenario 4: Adult with GI symptoms (possible comorbidities)",
            'symptoms': "burning chest pain after eating nausea stomach bloating",
            'patient': PatientProfile(age=45)
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print("\n" + "="*70)
        print(f"{scenario['name']}")
        print("="*70)
        print(f"\nSymptoms: {scenario['symptoms']}")
        
        # Patient info
        patient = scenario['patient']
        print(f"\nPatient Info:")
        print(f"  Age: {patient.age} years ({patient.age_group.value if patient.age_group else 'N/A'})")
        if patient.is_pregnant:
            print(f"  Status: Pregnant ⚠️")
        if patient.has_diabetes:
            print(f"  Comorbidity: Diabetes")
        
        # Analyze
        result = assistant.analyze_patient(scenario['symptoms'], patient)
        
        # Wait for user input between scenarios
        if i < len(scenarios):
            input("\n[Press Enter to continue to next scenario...]")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\n✅ All Priority 4 features demonstrated successfully!")
    print("\nAdvanced features include:")
    print("  ✅ Multi-disease detection with confidence scores")
    print("  ✅ Comorbidity pattern recognition")
    print("  ✅ Severity scoring (Emergency/Severe/Moderate/Mild)")
    print("  ✅ Patient-specific contraindications")
    print("  ✅ Age-appropriate dosing guidance")
    print("  ✅ Special population warnings (pregnancy, elderly, children)")
    print("  ✅ Comorbidity management recommendations")


def quick_test():
    """Quick test of a single scenario"""
    assistant = AdvancedHealthAssistant()
    
    print("\n" + "="*70)
    print("QUICK TEST - Emergency Scenario")
    print("="*70)
    
    symptoms = "crushing chest pain radiating to left arm severe sweating difficulty breathing"
    patient = PatientProfile(age=60, has_hypertension=True, has_diabetes=True)
    
    print(f"\nSymptoms: {symptoms}")
    print(f"Patient: {patient.age} year old with hypertension and diabetes")
    
    result = assistant.analyze_patient(symptoms, patient)
    
    print("\n" + "="*70)
    print("QUICK TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        interactive_demo()
