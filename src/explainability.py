"""
Explainability Module

Provides explanations for predictions by showing:
- Which symptoms matched the diagnosis
- Feature importance scores
- Confidence breakdown
"""

from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class SymptomMatcher:
    """Match input symptoms to diagnosis and explain the reasoning"""
    
    def __init__(self, vectorizer: TfidfVectorizer, model):
        self.vectorizer = vectorizer
        self.model = model
        self.feature_names = vectorizer.get_feature_names_out()
    
    def explain_prediction(self, symptoms: str, predicted_disease: str, confidence: float) -> Dict:
        """
        Explain why a prediction was made
        
        Returns:
            - matched_symptoms: List of symptoms that strongly matched
            - symptom_scores: Scores for each symptom
            - missing_symptoms: Common symptoms not mentioned
            - confidence_factors: What contributed to confidence
        """
        # Vectorize input
        symptoms_vec = self.vectorizer.transform([symptoms])
        symptoms_lower = symptoms.lower()
        
        # Get feature weights for this prediction
        feature_weights = self._get_feature_importance(symptoms_vec, predicted_disease)
        
        # Match symptoms to features
        matched, scores = self._match_symptoms_to_features(symptoms_lower, feature_weights)
        
        # Get common symptoms for this disease
        common_symptoms = self._get_disease_symptoms(predicted_disease)
        missing = [s for s in common_symptoms if s not in symptoms_lower]
        
        return {
            'matched_symptoms': matched,
            'symptom_scores': scores,
            'missing_symptoms': missing[:5],  # Top 5 missing
            'total_matches': len(matched),
            'confidence_breakdown': self._explain_confidence(confidence, len(matched), len(common_symptoms))
        }
    
    def _get_feature_importance(self, symptoms_vec, predicted_disease: str) -> Dict[str, float]:
        """Get importance scores for features in the prediction"""
        # Get model coefficients for predicted class
        try:
            if hasattr(self.model, 'base_estimator'):
                # CalibratedClassifierCV
                base_model = self.model.base_estimator
            else:
                base_model = self.model
            
            disease_classes = base_model.classes_
            if predicted_disease in disease_classes:
                class_idx = np.where(disease_classes == predicted_disease)[0][0]
                coef = base_model.coef_[class_idx]
                
                # Get feature importance
                feature_importance = {}
                symptoms_array = symptoms_vec.toarray()[0]
                
                for i, (feature, weight, present) in enumerate(zip(self.feature_names, coef, symptoms_array)):
                    if present > 0:  # Feature is in the input
                        importance = weight * present
                        feature_importance[feature] = float(importance)
                
                return dict(sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True))
        except:
            return {}
        
        return {}
    
    def _match_symptoms_to_features(self, symptoms_text: str, feature_weights: Dict[str, float]) -> Tuple[List[str], Dict[str, float]]:
        """Match recognized symptoms with their importance scores"""
        matched_symptoms = []
        scores = {}
        
        # Take top features
        for feature, weight in list(feature_weights.items())[:20]:
            if feature in symptoms_text:
                # Clean up feature name
                clean_feature = feature.replace('_', ' ').title()
                matched_symptoms.append(clean_feature)
                scores[clean_feature] = weight
        
        return matched_symptoms, scores
    
    def _get_disease_symptoms(self, disease: str) -> List[str]:
        """Get common symptoms for a disease (from knowledge base)"""
        # Common symptoms by disease (you can expand this)
        symptom_map = {
            'Influenza': ['fever', 'cough', 'body aches', 'headache', 'fatigue', 'sore throat'],
            'Common Cold': ['runny nose', 'sneezing', 'cough', 'sore throat', 'congestion'],
            'Migraine': ['headache', 'nausea', 'sensitivity to light', 'vomiting'],
            'Asthma': ['wheezing', 'shortness of breath', 'chest tightness', 'coughing'],
            'Diabetes': ['increased thirst', 'frequent urination', 'fatigue', 'blurred vision'],
            'Hypertension': ['headache', 'dizziness', 'shortness of breath', 'chest pain'],
            'Arthritis': ['joint pain', 'stiffness', 'swelling', 'reduced range of motion'],
            'Pneumonia': ['cough', 'fever', 'chest pain', 'difficulty breathing', 'fatigue'],
            'Bronchitis': ['cough', 'mucus production', 'fatigue', 'chest discomfort'],
            'Gastritis': ['stomach pain', 'nausea', 'bloating', 'indigestion'],
            'UTI': ['frequent urination', 'burning sensation', 'abdominal pain', 'cloudy urine'],
        }
        
        # Generic fallback
        return symptom_map.get(disease, ['fever', 'pain', 'discomfort', 'fatigue'])
    
    def _explain_confidence(self, confidence: float, matches: int, total_symptoms: int) -> Dict:
        """Break down what contributes to confidence score"""
        factors = []
        
        if confidence >= 0.75:
            factors.append(f"High confidence ({confidence:.1%}) - Strong symptom match")
        elif confidence >= 0.50:
            factors.append(f"Medium confidence ({confidence:.1%}) - Moderate symptom match")
        else:
            factors.append(f"Low confidence ({confidence:.1%}) - Weak or ambiguous symptoms")
        
        match_rate = matches / total_symptoms if total_symptoms > 0 else 0
        if match_rate >= 0.7:
            factors.append(f"Matched {matches}/{total_symptoms} key symptoms ({match_rate:.0%})")
        elif match_rate >= 0.4:
            factors.append(f"Matched {matches}/{total_symptoms} key symptoms ({match_rate:.0%}) - Some symptoms missing")
        else:
            factors.append(f"Only {matches}/{total_symptoms} symptoms matched ({match_rate:.0%}) - Diagnosis uncertain")
        
        return {
            'overall_confidence': confidence,
            'match_rate': match_rate,
            'factors': factors,
            'recommendation': self._get_recommendation(confidence, match_rate)
        }
    
    def _get_recommendation(self, confidence: float, match_rate: float) -> str:
        """Provide recommendation based on confidence"""
        if confidence < 0.5 or match_rate < 0.5:
            return "⚠️ Low confidence - Please consult a healthcare professional for accurate diagnosis"
        elif confidence < 0.75:
            return "ℹ️ Moderate confidence - Consider medical consultation if symptoms persist"
        else:
            return "✅ High confidence - This appears to be a good match based on your symptoms"


def format_explainability_output(explanation: Dict) -> str:
    """Format explanation for display"""
    output = []
    
    output.append("=" * 70)
    output.append("WHY THIS DIAGNOSIS?")
    output.append("=" * 70)
    
    # Matched symptoms
    if explanation['matched_symptoms']:
        output.append("\n✅ SYMPTOMS THAT MATCHED:")
        for symptom in explanation['matched_symptoms'][:10]:
            score = explanation['symptom_scores'].get(symptom, 0)
            # Create bar visualization
            bar_length = int(abs(score) * 20)
            bar = "█" * min(bar_length, 20)
            output.append(f"   • {symptom:<30s} {bar} {abs(score):.2f}")
    
    # Missing symptoms
    if explanation['missing_symptoms']:
        output.append("\n⚠️  COMMON SYMPTOMS NOT MENTIONED:")
        for symptom in explanation['missing_symptoms']:
            output.append(f"   • {symptom}")
        output.append("\n   💡 TIP: Mention these if you're experiencing them for better accuracy")
    
    # Confidence breakdown
    breakdown = explanation['confidence_breakdown']
    output.append(f"\n📊 CONFIDENCE ANALYSIS:")
    output.append(f"   Overall Confidence: {breakdown['overall_confidence']:.1%}")
    output.append(f"   Symptom Match Rate: {breakdown['match_rate']:.1%}")
    output.append(f"\n   {breakdown['recommendation']}")
    
    output.append("\n" + "=" * 70)
    
    return "\n".join(output)


def create_symptom_importance_chart(explanation: Dict, top_n: int = 10):
    """Create data for symptom importance visualization (for Streamlit)"""
    import pandas as pd
    
    symptoms = []
    scores = []
    
    for symptom, score in list(explanation['symptom_scores'].items())[:top_n]:
        symptoms.append(symptom)
        scores.append(abs(score))
    
    return pd.DataFrame({
        'Symptom': symptoms,
        'Importance': scores
    })


if __name__ == "__main__":
    # Example usage (would normally use real model)
    print("Explainability module loaded successfully!")
    
    # Mock explanation
    mock_explanation = {
        'matched_symptoms': ['Fever', 'Headache', 'Body Aches', 'Cough'],
        'symptom_scores': {
            'Fever': 2.5,
            'Headache': 1.8,
            'Body Aches': 1.6,
            'Cough': 1.2
        },
        'missing_symptoms': ['Sore Throat', 'Fatigue'],
        'total_matches': 4,
        'confidence_breakdown': {
            'overall_confidence': 0.85,
            'match_rate': 0.67,
            'factors': [
                'High confidence (85%) - Strong symptom match',
                'Matched 4/6 key symptoms (67%)'
            ],
            'recommendation': '✅ High confidence - This appears to be a good match'
        }
    }
    
    print(format_explainability_output(mock_explanation))
