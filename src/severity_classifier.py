"""
Symptom Severity Scoring System

Classifies symptoms as Mild, Moderate, or Severe based on:
- Keyword intensity (severe, extreme, unbearable)
- Emergency indicators
- Duration and progression
- Functional impact
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class SeverityScore:
    """Container for severity assessment"""
    level: str  # "Mild", "Moderate", "Severe", "Emergency"
    score: int  # 0-100
    factors: List[str]  # Contributing factors
    recommendations: List[str]  # Action items
    urgent: bool  # Requires immediate attention

class SeverityClassifier:
    """Classify symptom severity"""
    
    def __init__(self):
        # Emergency keywords (highest priority)
        self.emergency_keywords = {
            'chest pain', 'crushing chest', 'radiating pain', 'left arm pain',
            'sudden weakness', 'facial drooping', 'slurred speech',
            'difficulty breathing', 'cant breathe', 'gasping',
            'severe bleeding', 'heavy bleeding', 'bleeding wont stop',
            'unconscious', 'unresponsive', 'seizure', 'convulsion',
            'severe headache', 'worst headache', 'thunderclap',
            'confusion', 'disoriented', 'altered consciousness',
            'severe allergic', 'throat swelling', 'anaphylaxis',
            'poisoning', 'overdose', 'suicide'
        }
        
        # Severe intensity keywords
        self.severe_keywords = {
            'severe', 'extreme', 'excruciating', 'unbearable', 'agonizing',
            'intense', 'terrible', 'horrible', 'worst', 'acute',
            'massive', 'violent', 'crushing', 'stabbing', 'shooting'
        }
        
        # Moderate intensity keywords
        self.moderate_keywords = {
            'moderate', 'significant', 'considerable', 'noticeable',
            'persistent', 'constant', 'ongoing', 'worsening',
            'recurrent', 'frequent', 'regular', 'chronic'
        }
        
        # Mild intensity keywords
        self.mild_keywords = {
            'mild', 'slight', 'minor', 'little', 'small',
            'occasional', 'intermittent', 'sometimes', 'rare'
        }
        
        # Duration indicators (longer = more severe)
        self.duration_severe = {
            'weeks', 'months', 'years', 'long time', 'forever',
            'constantly', 'always', 'never stops'
        }
        
        self.duration_moderate = {
            'days', 'several days', 'week', 'one week'
        }
        
        # Functional impact (severe)
        self.impact_severe = {
            'cant walk', 'cant stand', 'cant move', 'cant eat',
            'cant sleep', 'cant work', 'bedridden', 'disabled',
            'unable to', 'impossible to', 'cant breathe'
        }
        
        # Progressive symptoms (concerning)
        self.progression_keywords = {
            'getting worse', 'worsening', 'spreading', 'increasing',
            'progressively', 'deteriorating', 'declining'
        }
    
    def analyze_severity(self, symptoms: str, disease: str = None) -> SeverityScore:
        """
        Analyze symptom severity
        
        Args:
            symptoms: Patient symptom description
            disease: Detected disease (optional, for context)
        
        Returns:
            SeverityScore object with level and recommendations
        """
        symptoms_lower = symptoms.lower()
        score = 0
        factors = []
        
        # Check for emergency keywords (immediate override)
        emergency_matches = [kw for kw in self.emergency_keywords if kw in symptoms_lower]
        if emergency_matches:
            return SeverityScore(
                level="Emergency",
                score=100,
                factors=[f"Emergency keyword: '{kw}'" for kw in emergency_matches],
                recommendations=[
                    "🚨 CALL EMERGENCY SERVICES IMMEDIATELY (911/112/108)",
                    "Do not wait or drive yourself",
                    "Time is critical for this condition"
                ],
                urgent=True
            )
        
        # Score severe keywords (+30 points each, max 60)
        severe_matches = [kw for kw in self.severe_keywords if kw in symptoms_lower]
        if severe_matches:
            score += min(len(severe_matches) * 30, 60)
            factors.extend([f"Severe intensity: '{kw}'" for kw in severe_matches[:2]])
        
        # Score moderate keywords (+15 points each, max 30)
        moderate_matches = [kw for kw in self.moderate_keywords if kw in symptoms_lower]
        if moderate_matches:
            score += min(len(moderate_matches) * 15, 30)
            factors.extend([f"Moderate intensity: '{kw}'" for kw in moderate_matches[:2]])
        
        # Score mild keywords (-10 points, but never below 0)
        mild_matches = [kw for kw in self.mild_keywords if kw in symptoms_lower]
        if mild_matches:
            score = max(0, score - 10)
            factors.append(f"Mild indicator: '{mild_matches[0]}'")
        
        # Score duration (longer = worse)
        duration_severe_matches = [kw for kw in self.duration_severe if kw in symptoms_lower]
        if duration_severe_matches:
            score += 20
            factors.append(f"Chronic duration: '{duration_severe_matches[0]}'")
        
        duration_moderate_matches = [kw for kw in self.duration_moderate if kw in symptoms_lower]
        if duration_moderate_matches and not duration_severe_matches:
            score += 10
            factors.append(f"Extended duration: '{duration_moderate_matches[0]}'")
        
        # Score functional impact (+40 points)
        impact_matches = [kw for kw in self.impact_severe if kw in symptoms_lower]
        if impact_matches:
            score += 40
            factors.extend([f"Functional impact: '{kw}'" for kw in impact_matches[:2]])
        
        # Score progression (+20 points)
        progression_matches = [kw for kw in self.progression_keywords if kw in symptoms_lower]
        if progression_matches:
            score += 20
            factors.append(f"Progressive: '{progression_matches[0]}'")
        
        # Disease-specific severity adjustments
        if disease:
            disease_adjustment = self._get_disease_severity(disease, symptoms_lower)
            score += disease_adjustment
            if disease_adjustment > 0:
                factors.append(f"Disease severity factor: {disease} (+{disease_adjustment})")
        
        # Default minimum score if no keywords found
        if score == 0 and not factors:
            score = 20  # Baseline "mild" score
            factors.append("No severity indicators found (assumed mild)")
        
        # Determine level and recommendations
        return self._score_to_severity(score, factors)
    
    def _get_disease_severity(self, disease: str, symptoms: str) -> int:
        """Adjust score based on disease-specific factors"""
        # Life-threatening conditions
        if disease in ['Heart Attack', 'Stroke', 'Sepsis', 'Meningitis', 'Anaphylaxis']:
            return 50  # Already emergency level
        
        # Serious chronic conditions
        if disease in ['Diabetes', 'Hypertension', 'Tuberculosis']:
            # Check for complications
            if 'uncontrolled' in symptoms or 'very high' in symptoms:
                return 20
            return 10
        
        # Infectious diseases with fever
        if disease in ['Malaria', 'Dengue', 'Typhoid', 'Pneumonia']:
            if 'high fever' in symptoms or 'very high fever' in symptoms:
                return 15
            return 5
        
        return 0
    
    def _score_to_severity(self, score: int, factors: List[str]) -> SeverityScore:
        """Convert numeric score to severity level"""
        
        if score >= 80:
            return SeverityScore(
                level="Severe",
                score=score,
                factors=factors,
                recommendations=[
                    "🏥 SEEK IMMEDIATE MEDICAL ATTENTION",
                    "Visit emergency room or urgent care today",
                    "Do not delay treatment",
                    "Monitor symptoms closely"
                ],
                urgent=True
            )
        
        elif score >= 50:
            return SeverityScore(
                level="Moderate-Severe",
                score=score,
                factors=factors,
                recommendations=[
                    "⚠️ MEDICAL CONSULTATION RECOMMENDED",
                    "Schedule doctor appointment within 24-48 hours",
                    "Monitor for worsening symptoms",
                    "Avoid strenuous activities"
                ],
                urgent=True
            )
        
        elif score >= 30:
            return SeverityScore(
                level="Moderate",
                score=score,
                factors=factors,
                recommendations=[
                    "📋 MEDICAL ADVICE RECOMMENDED",
                    "Consider scheduling doctor appointment this week",
                    "Track symptoms and progression",
                    "Rest and stay hydrated"
                ],
                urgent=False
            )
        
        else:
            return SeverityScore(
                level="Mild",
                score=score,
                factors=factors,
                recommendations=[
                    "✅ SELF-CARE APPROPRIATE",
                    "Monitor symptoms over next few days",
                    "Seek medical advice if symptoms worsen or persist",
                    "Rest, hydration, and over-the-counter remedies may help"
                ],
                urgent=False
            )


def format_severity_output(severity: SeverityScore) -> str:
    """Format severity score for display"""
    output = []
    
    output.append("="*70)
    output.append("SYMPTOM SEVERITY ASSESSMENT")
    output.append("="*70)
    
    # Severity level with color coding
    level_icons = {
        "Emergency": "🚨",
        "Severe": "🔴",
        "Moderate-Severe": "🟠",
        "Moderate": "🟡",
        "Mild": "🟢"
    }
    
    icon = level_icons.get(severity.level, "⚪")
    output.append(f"\n{icon} SEVERITY LEVEL: {severity.level.upper()}")
    output.append(f"   Severity Score: {severity.score}/100")
    
    if severity.urgent:
        output.append(f"   ⚠️ URGENT: Requires prompt medical attention")
    
    # Factors
    if severity.factors:
        output.append(f"\n📊 CONTRIBUTING FACTORS:")
        for factor in severity.factors[:5]:  # Limit to top 5
            output.append(f"   • {factor}")
    
    # Recommendations
    output.append(f"\n💡 RECOMMENDED ACTIONS:")
    for rec in severity.recommendations:
        output.append(f"   {rec}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test severity classifier
    classifier = SeverityClassifier()
    
    print("Testing Symptom Severity Classifier")
    print("="*70)
    
    # Test Case 1: Emergency
    print("\n\nTest 1: Emergency symptoms")
    print("-"*70)
    symptoms1 = "severe crushing chest pain radiating to left arm cant breathe"
    severity1 = classifier.analyze_severity(symptoms1, "Heart Attack")
    print(f"Symptoms: {symptoms1}")
    print(format_severity_output(severity1))
    
    # Test Case 2: Severe
    print("\n\nTest 2: Severe symptoms")
    print("-"*70)
    symptoms2 = "extreme abdominal pain for several days getting worse cant eat"
    severity2 = classifier.analyze_severity(symptoms2, "Appendicitis")
    print(f"Symptoms: {symptoms2}")
    print(format_severity_output(severity2))
    
    # Test Case 3: Moderate
    print("\n\nTest 3: Moderate symptoms")
    print("-"*70)
    symptoms3 = "persistent headache and fatigue for one week"
    severity3 = classifier.analyze_severity(symptoms3, "Migraine")
    print(f"Symptoms: {symptoms3}")
    print(format_severity_output(severity3))
    
    # Test Case 4: Mild
    print("\n\nTest 4: Mild symptoms")
    print("-"*70)
    symptoms4 = "slight runny nose occasional sneezing"
    severity4 = classifier.analyze_severity(symptoms4, "Common Cold")
    print(f"Symptoms: {symptoms4}")
    print(format_severity_output(severity4))
    
    # Test Case 5: Chronic severe
    print("\n\nTest 5: Chronic condition")
    print("-"*70)
    symptoms5 = "chronic joint pain for months constant stiffness unable to walk properly"
    severity5 = classifier.analyze_severity(symptoms5, "Rheumatoid Arthritis")
    print(f"Symptoms: {symptoms5}")
    print(format_severity_output(severity5))
