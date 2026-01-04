"""
Advanced Multi-Disease Detection System

Detects multiple diseases that a patient may have simultaneously.
Returns top-N predictions with confidence scores.
"""

import joblib
import re
from typing import List, Dict, Tuple

class MultiDiseaseDetector:
    """Detect multiple diseases from symptoms"""
    
    def __init__(self, model_path="data/symptom_model.pkl"):
        """Load the trained model"""
        self.vectorizer, self.model = joblib.load(model_path)
        self.disease_classes = self.model.classes_
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize symptom text"""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def predict_multiple(
        self, 
        symptoms: str, 
        top_n: int = 3, 
        min_confidence: float = 0.15
    ) -> List[Dict]:
        """
        Predict multiple diseases from symptoms
        
        Args:
            symptoms: Patient symptom description
            top_n: Maximum number of diseases to return
            min_confidence: Minimum confidence threshold (default 15%)
        
        Returns:
            List of disease predictions with confidence scores
        """
        # Clean symptoms
        symptoms_clean = self.clean_text(symptoms)
        
        # Vectorize
        symptoms_vec = self.vectorizer.transform([symptoms_clean])
        
        # Get probabilities for all diseases
        probabilities = self.model.predict_proba(symptoms_vec)[0]
        
        # Get top-N predictions
        top_indices = probabilities.argsort()[-top_n:][::-1]
        
        predictions = []
        for idx in top_indices:
            confidence = probabilities[idx]
            
            # Only include if above minimum confidence
            if confidence >= min_confidence:
                predictions.append({
                    'disease': self.disease_classes[idx],
                    'confidence': float(confidence),
                    'confidence_level': self._get_confidence_level(confidence),
                    'rank': len(predictions) + 1
                })
        
        return predictions
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level"""
        if confidence >= 0.75:
            return "High"
        elif confidence >= 0.45:
            return "Medium"
        else:
            return "Low"
    
    def detect_comorbidities(self, symptoms: str) -> Dict:
        """
        Detect if patient likely has multiple conditions
        
        Returns:
            Dict with primary disease, possible comorbidities, and flags
        """
        # Chronic diseases that CANNOT be inferred from acute symptoms alone
        CHRONIC_DISEASES_EXCLUDE = {
            'Hypertension', 'Diabetes', 'Chronic Kidney Disease', 
            'Heart Disease', 'Arthritis', 'COPD', 'Asthma'
        }
        
        predictions = self.predict_multiple(symptoms, top_n=5, min_confidence=0.10)
        
        # Filter out chronic diseases unless confidence is very high (>60%)
        filtered_predictions = []
        for pred in predictions:
            disease = pred['disease']
            conf = pred['confidence']
            # Only include chronic diseases if confidence > 60%
            if disease in CHRONIC_DISEASES_EXCLUDE and conf < 0.60:
                continue
            filtered_predictions.append(pred)
        
        predictions = filtered_predictions
        
        if not predictions:
            return {
                'primary_disease': None,
                'comorbidities': [],
                'has_multiple_conditions': False,
                'confidence_gap': 0.0
            }
        
        primary = predictions[0]
        comorbidities = []
        
        # Check for comorbidities based on confidence gap
        if len(predictions) > 1:
            secondary = predictions[1]
            confidence_gap = primary['confidence'] - secondary['confidence']
            
            # If gap is small (<0.20), likely multiple conditions
            if confidence_gap < 0.20 and secondary['confidence'] > 0.20:
                comorbidities = predictions[1:]
        
        return {
            'primary_disease': primary,
            'comorbidities': comorbidities,
            'has_multiple_conditions': len(comorbidities) > 0,
            'confidence_gap': confidence_gap if len(predictions) > 1 else 1.0,
            'all_predictions': predictions
        }
    
    def analyze_symptom_overlap(self, symptoms: str) -> Dict:
        """
        Analyze which symptoms might indicate multiple conditions
        
        Common comorbidity patterns:
        - Diabetes + Hypertension
        - Asthma + Allergic Reaction
        - GERD + Peptic Ulcer
        - Arthritis + Osteoarthritis
        """
        result = self.detect_comorbidities(symptoms)
        
        if not result['has_multiple_conditions']:
            return result
        
        # Add comorbidity pattern analysis
        primary_name = result['primary_disease']['disease']
        comorbid_names = [c['disease'] for c in result['comorbidities']]
        
        # Known comorbidity patterns
        patterns = {
            ('Diabetes', 'Hypertension'): 'Common metabolic comorbidity',
            ('Asthma', 'Allergic Reaction'): 'Allergic/respiratory overlap',
            ('GERD', 'Peptic Ulcer'): 'Gastrointestinal conditions',
            ('Rheumatoid Arthritis', 'Osteoarthritis'): 'Joint conditions',
            ('COVID-19', 'Pneumonia'): 'Respiratory infection progression',
            ('Hypothyroidism', 'Hyperthyroidism'): 'Thyroid disorder (check again)',
        }
        
        result['comorbidity_pattern'] = None
        for (disease1, disease2), description in patterns.items():
            diseases = [primary_name] + comorbid_names
            if disease1 in diseases and disease2 in diseases:
                result['comorbidity_pattern'] = {
                    'pattern': f"{disease1} + {disease2}",
                    'description': description,
                    'recommendation': 'Comprehensive evaluation recommended'
                }
                break
        
        return result


def format_multi_disease_output(result: Dict) -> str:
    """Format multi-disease detection results for display"""
    output = []
    
    output.append("="*70)
    output.append("MULTI-DISEASE ANALYSIS")
    output.append("="*70)
    
    # Primary disease
    primary = result['primary_disease']
    if primary:
        output.append(f"\n🎯 PRIMARY DIAGNOSIS:")
        output.append(f"   Disease: {primary['disease']}")
        output.append(f"   Confidence: {primary['confidence']*100:.1f}% ({primary['confidence_level']})")
    
    # Comorbidities
    if result['has_multiple_conditions']:
        output.append(f"\n⚠️  POSSIBLE COMORBIDITIES DETECTED:")
        output.append(f"   Confidence gap: {result['confidence_gap']*100:.1f}%")
        output.append(f"   (Small gap suggests multiple conditions)")
        
        for i, comorbid in enumerate(result['comorbidities'], 1):
            output.append(f"\n   {i}. {comorbid['disease']}")
            output.append(f"      Confidence: {comorbid['confidence']*100:.1f}% ({comorbid['confidence_level']})")
        
        # Pattern analysis
        if result.get('comorbidity_pattern'):
            pattern = result['comorbidity_pattern']
            output.append(f"\n📊 COMORBIDITY PATTERN:")
            output.append(f"   {pattern['pattern']}")
            output.append(f"   Type: {pattern['description']}")
            output.append(f"   💡 {pattern['recommendation']}")
    else:
        output.append(f"\n✅ SINGLE CONDITION LIKELY")
        output.append(f"   Confidence gap: {result['confidence_gap']*100:.1f}%")
        output.append(f"   (Large gap suggests single condition)")
    
    # All predictions
    output.append(f"\n📋 ALL PREDICTIONS (Top {len(result['all_predictions'])})")
    for i, pred in enumerate(result['all_predictions'], 1):
        conf_bar = "█" * int(pred['confidence'] * 30)
        output.append(f"   {i}. {pred['disease']:<30} {conf_bar} {pred['confidence']*100:.1f}%")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test multi-disease detection
    detector = MultiDiseaseDetector()
    
    print("Testing Multi-Disease Detection System")
    print("="*70)
    
    # Test Case 1: Single clear condition
    print("\n\nTest 1: Clear single condition")
    print("-"*70)
    symptoms1 = "severe chest pain radiating to left arm with sweating"
    result1 = detector.analyze_symptom_overlap(symptoms1)
    print(f"Symptoms: {symptoms1}")
    print(format_multi_disease_output(result1))
    
    # Test Case 2: Overlapping symptoms (Diabetes + Hypertension)
    print("\n\nTest 2: Multiple conditions (metabolic)")
    print("-"*70)
    symptoms2 = "frequent urination increased thirst blurred vision high blood pressure headache"
    result2 = detector.analyze_symptom_overlap(symptoms2)
    print(f"Symptoms: {symptoms2}")
    print(format_multi_disease_output(result2))
    
    # Test Case 3: Respiratory overlap
    print("\n\nTest 3: Respiratory conditions")
    print("-"*70)
    symptoms3 = "difficulty breathing wheezing cough chest tightness itchy skin rash"
    result3 = detector.analyze_symptom_overlap(symptoms3)
    print(f"Symptoms: {symptoms3}")
    print(format_multi_disease_output(result3))
    
    # Test Case 4: GI overlap
    print("\n\nTest 4: Gastrointestinal conditions")
    print("-"*70)
    symptoms4 = "burning chest pain after eating nausea stomach pain bloating"
    result4 = detector.analyze_symptom_overlap(symptoms4)
    print(f"Symptoms: {symptoms4}")
    print(format_multi_disease_output(result4))
