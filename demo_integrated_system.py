"""
Quick Demo of Advanced Features Integration in Main System

This demonstrates how advanced features work with patient profiles.
"""

import sys
sys.path.append('/workspaces/Cure-Blend')

from src.ai_assistant import load_knowledge_base, generate_comprehensive_answer
from src.multi_disease_detector import MultiDiseaseDetector, format_multi_disease_output
from src.severity_classifier import SeverityClassifier, format_severity_output
from src.personalized_recommender import (
    PersonalizedRecommender,
    PatientProfile,
    format_personalized_output
)

def demo_advanced_integration():
    """Demonstrate complete system with advanced features"""
    
    print("="*70)
    print("ADVANCED FEATURES - INTEGRATED DEMO")
    print("="*70)
    
    # Load system
    print("\n📚 Loading system...")
    knowledge = load_knowledge_base()
    print("✅ System loaded!\n")
    
    # Demo scenarios
    scenarios = [
        {
            'name': "Pregnant Woman with UTI",
            'symptoms': "frequent urination burning sensation lower abdominal discomfort",
            'patient': PatientProfile(age=28, gender="female", is_pregnant=True)
        },
        {
            'name': "Elderly with Respiratory Symptoms",
            'symptoms': "severe difficulty breathing chest tightness persistent cough",
            'patient': PatientProfile(age=72, has_diabetes=True, has_hypertension=True)
        },
        {
            'name': "Child with Fever",
            'symptoms': "high fever headache body aches",
            'patient': PatientProfile(age=8)
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print("="*70)
        print(f"SCENARIO {i}: {scenario['name']}")
        print("="*70)
        print(f"\n💬 Symptoms: {scenario['symptoms']}")
        
        patient = scenario['patient']
        print(f"\n👤 Patient:")
        print(f"   Age: {patient.age} years")
        if patient.is_pregnant:
            print(f"   Status: ⚠️  Pregnant")
        if patient.has_diabetes:
            print(f"   Condition: Diabetes")
        if patient.has_hypertension:
            print(f"   Condition: Hypertension")
        
        print(f"\n🔍 Running Analysis...")
        
        # Step 1: Basic prediction
        response = generate_comprehensive_answer(
            scenario['symptoms'],
            knowledge,
            use_ai=False,
            include_drugs=True
        )
        
        primary_disease = response.get('disease', 'Unknown')
        primary_confidence = response.get('confidence', 0.5)
        
        print(f"✅ Primary Diagnosis: {primary_disease} ({primary_confidence*100:.1f}%)")
        
        # Step 2: Multi-disease detection
        detector = MultiDiseaseDetector()
        disease_analysis = detector.analyze_symptom_overlap(scenario['symptoms'])
        
        if disease_analysis['has_multiple_conditions']:
            print(f"⚠️  Comorbidities detected: {len(disease_analysis['comorbidities'])}")
        
        # Step 3: Severity assessment
        severity_classifier = SeverityClassifier()
        severity = severity_classifier.analyze_severity(scenario['symptoms'], primary_disease)
        
        print(f"🚨 Severity: {severity.level} ({severity.score}/100)")
        
        # Step 4: Personalized recommendations
        recommender = PersonalizedRecommender()
        recommendations = recommender.personalize_recommendations(
            disease=primary_disease,
            severity_level=severity.level,
            patient=patient
        )
        
        print(f"⚠️  Warnings: {len(recommendations['warnings'])}")
        print(f"❌ Contraindications: {len(recommendations['contraindications'])}")
        
        # Show detailed results
        print("\n" + "="*70)
        print("DETAILED ANALYSIS")
        print("="*70)
        
        print(format_multi_disease_output(disease_analysis))
        print(format_severity_output(severity))
        print(format_personalized_output(recommendations))
        
        if i < len(scenarios):
            input("\n[Press Enter to continue to next scenario...]")
        print("\n")
    
    print("="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\n✅ All advanced features working correctly!")
    print("\nTo use in main system:")
    print("  1. Run: python main.py")
    print("  2. Answer 'y' to: Use advanced features?")
    print("  3. Answer 'y' to: Create patient profile?")
    print("  4. Fill in patient information")
    print("  5. Enter symptoms")
    print("\nThe system will show:")
    print("  • Basic herbal + pharmaceutical recommendations")
    print("  • Multi-disease analysis")
    print("  • Severity scoring")
    print("  • Personalized safety warnings")


if __name__ == "__main__":
    try:
        demo_advanced_integration()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
