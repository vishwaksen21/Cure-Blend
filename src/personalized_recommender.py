"""
Personalized Recommendations Engine

Adjusts treatment recommendations based on:
- Patient demographics (age, gender)
- Special populations (pregnancy, breastfeeding, elderly, children)
- Severity level
- Comorbidities
- Contraindications
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgeGroup(Enum):
    """Age classifications"""
    INFANT = "infant"  # 0-2 years
    CHILD = "child"  # 3-12 years
    TEEN = "teen"  # 13-17 years
    ADULT = "adult"  # 18-64 years
    ELDERLY = "elderly"  # 65+ years

class SpecialPopulation(Enum):
    """Special patient populations"""
    PREGNANT = "pregnant"
    BREASTFEEDING = "breastfeeding"
    ELDERLY = "elderly"
    CHILDREN = "children"
    DIABETIC = "diabetic"
    HYPERTENSIVE = "hypertensive"
    KIDNEY_DISEASE = "kidney_disease"
    LIVER_DISEASE = "liver_disease"

@dataclass
class PatientProfile:
    """Patient information for personalization"""
    age: Optional[int] = None
    age_group: Optional[AgeGroup] = None
    gender: Optional[str] = None
    is_pregnant: bool = False
    is_breastfeeding: bool = False
    has_diabetes: bool = False
    has_hypertension: bool = False
    has_kidney_disease: bool = False
    has_liver_disease: bool = False
    known_allergies: List[str] = None
    current_medications: List[str] = None
    
    def __post_init__(self):
        if self.known_allergies is None:
            self.known_allergies = []
        if self.current_medications is None:
            self.current_medications = []
        
        # Auto-determine age group from age
        if self.age and not self.age_group:
            if self.age < 3:
                self.age_group = AgeGroup.INFANT
            elif self.age < 13:
                self.age_group = AgeGroup.CHILD
            elif self.age < 18:
                self.age_group = AgeGroup.TEEN
            elif self.age < 65:
                self.age_group = AgeGroup.ADULT
            else:
                self.age_group = AgeGroup.ELDERLY
    
    def get_special_populations(self) -> List[SpecialPopulation]:
        """Get list of special population categories"""
        populations = []
        
        if self.is_pregnant:
            populations.append(SpecialPopulation.PREGNANT)
        if self.is_breastfeeding:
            populations.append(SpecialPopulation.BREASTFEEDING)
        if self.age_group in [AgeGroup.INFANT, AgeGroup.CHILD]:
            populations.append(SpecialPopulation.CHILDREN)
        if self.age_group == AgeGroup.ELDERLY:
            populations.append(SpecialPopulation.ELDERLY)
        if self.has_diabetes:
            populations.append(SpecialPopulation.DIABETIC)
        if self.has_hypertension:
            populations.append(SpecialPopulation.HYPERTENSIVE)
        if self.has_kidney_disease:
            populations.append(SpecialPopulation.KIDNEY_DISEASE)
        if self.has_liver_disease:
            populations.append(SpecialPopulation.LIVER_DISEASE)
        
        return populations


class PersonalizedRecommender:
    """Generate personalized treatment recommendations"""
    
    def __init__(self):
        # Drug contraindications for special populations
        self.contraindications = {
            SpecialPopulation.PREGNANT: {
                'avoid': [
                    'NSAIDs (after 20 weeks)', 'ACE inhibitors', 'ARBs',
                    'Tetracyclines', 'Fluoroquinolones', 'Statins',
                    'Warfarin', 'Isotretinoin', 'Certain antibiotics'
                ],
                'caution': [
                    'Paracetamol (limited use)', 'Some antibiotics',
                    'Antacids (aluminum-free)', 'Cough suppressants'
                ]
            },
            SpecialPopulation.BREASTFEEDING: {
                'avoid': [
                    'Aspirin', 'Certain antibiotics', 'Antihistamines (sedating)',
                    'Decongestants (may reduce milk)', 'Some antidepressants'
                ],
                'caution': [
                    'NSAIDs (short-term only)', 'Paracetamol (safe)',
                    'Certain antibiotics (safe)', 'Monitor infant for effects'
                ]
            },
            SpecialPopulation.CHILDREN: {
                'avoid': [
                    'Aspirin (<16 years - Reye syndrome risk)',
                    'Adult formulations', 'Certain cough medicines (<6 years)'
                ],
                'caution': [
                    'Dose by weight, not age', 'Use pediatric formulations',
                    'Avoid honey <1 year', 'Monitor for adverse reactions'
                ]
            },
            SpecialPopulation.ELDERLY: {
                'avoid': [
                    'Benzodiazepines (fall risk)', 'Anticholinergics',
                    'NSAIDs (bleeding risk)', 'Multiple sedatives'
                ],
                'caution': [
                    'Start low, go slow', 'Check kidney function',
                    'Watch for drug interactions', 'Monitor side effects'
                ]
            },
            SpecialPopulation.DIABETIC: {
                'avoid': [
                    'Corticosteroids (raise blood sugar)', 'Thiazide diuretics',
                    'Beta-blockers (mask hypoglycemia)'
                ],
                'caution': [
                    'Monitor blood glucose closely', 'Adjust insulin doses',
                    'Avoid drugs that affect glucose', 'Check HbA1c regularly'
                ]
            },
            SpecialPopulation.KIDNEY_DISEASE: {
                'avoid': [
                    'NSAIDs', 'Certain antibiotics (nephrotoxic)',
                    'Metformin (if eGFR <30)', 'Contrast dyes'
                ],
                'caution': [
                    'Adjust doses for kidney function', 'Monitor creatinine',
                    'Avoid nephrotoxic drugs', 'Stay hydrated'
                ]
            }
        }
        
        # Severity-based adjustments
        self.severity_modifications = {
            'Emergency': {
                'message': '🚨 EMERGENCY: Call ambulance immediately',
                'self_care': False,
                'otc_allowed': False,
                'immediate_action': 'Emergency services required NOW'
            },
            'Severe': {
                'message': '🏥 Immediate medical attention required',
                'self_care': False,
                'otc_allowed': False,
                'immediate_action': 'Visit ER or urgent care today'
            },
            'Moderate-Severe': {
                'message': '⚠️ Medical consultation needed soon',
                'self_care': False,
                'otc_allowed': True,
                'immediate_action': 'See doctor within 24-48 hours'
            },
            'Moderate': {
                'message': '📋 Medical advice recommended',
                'self_care': True,
                'otc_allowed': True,
                'immediate_action': 'Schedule doctor appointment this week'
            },
            'Mild': {
                'message': '✅ Self-care appropriate',
                'self_care': True,
                'otc_allowed': True,
                'immediate_action': 'Monitor and self-care'
            }
        }
    
    def personalize_recommendations(
        self,
        disease: str,
        severity_level: str,
        patient: PatientProfile,
        drugs: List[Dict] = None,
        herbs: List[Dict] = None
    ) -> Dict:
        """
        Generate personalized recommendations
        
        Args:
            disease: Detected disease
            severity_level: Severity classification
            patient: Patient profile
            drugs: List of pharmaceutical options
            herbs: List of herbal options
        
        Returns:
            Personalized recommendations with warnings and adjustments
        """
        recommendations = {
            'disease': disease,
            'severity': severity_level,
            'patient_populations': [p.value for p in patient.get_special_populations()],
            'warnings': [],
            'contraindications': [],
            'dose_adjustments': [],
            'safe_drugs': [],
            'avoid_drugs': [],
            'safe_herbs': [],
            'caution_herbs': [],
            'lifestyle_advice': [],
            'immediate_actions': []
        }
        
        # Get severity-based modifications
        severity_mod = self.severity_modifications.get(severity_level, {})
        if severity_mod:
            recommendations['severity_message'] = severity_mod['message']
            recommendations['immediate_actions'].append(severity_mod['immediate_action'])
            recommendations['self_care_appropriate'] = severity_mod['self_care']
            recommendations['otc_allowed'] = severity_mod['otc_allowed']
        
        # Process contraindications for special populations
        for population in patient.get_special_populations():
            if population in self.contraindications:
                contras = self.contraindications[population]
                
                # Add warnings
                recommendations['warnings'].append({
                    'population': population.value,
                    'type': 'Special Population',
                    'message': f"Patient is {population.value} - special precautions required"
                })
                
                # Add contraindications
                recommendations['contraindications'].extend([
                    {'drug': drug, 'reason': f'Contraindicated in {population.value}'}
                    for drug in contras.get('avoid', [])
                ])
                
                # Add cautions
                for caution in contras.get('caution', []):
                    recommendations['dose_adjustments'].append({
                        'note': caution,
                        'population': population.value
                    })
        
        # Age-specific adjustments
        if patient.age_group:
            age_advice = self._get_age_specific_advice(patient.age_group, disease)
            recommendations['lifestyle_advice'].extend(age_advice)
        
        # Filter drugs based on contraindications
        if drugs:
            for drug in drugs:
                drug_name = drug.get('name', '').lower()
                is_contraindicated = False
                
                # Check against contraindication list
                for contra in recommendations['contraindications']:
                    if any(term in drug_name for term in contra['drug'].lower().split()):
                        is_contraindicated = True
                        recommendations['avoid_drugs'].append({
                            **drug,
                            'reason': contra['reason']
                        })
                        break
                
                if not is_contraindicated:
                    recommendations['safe_drugs'].append(drug)
        
        # Filter herbs
        if herbs:
            for herb in herbs:
                herb_name = herb.get('name', '').lower()
                
                # General herb cautions
                if patient.is_pregnant:
                    recommendations['caution_herbs'].append({
                        **herb,
                        'warning': 'Use with caution during pregnancy - consult herbalist'
                    })
                elif patient.age_group in [AgeGroup.INFANT, AgeGroup.CHILD]:
                    recommendations['caution_herbs'].append({
                        **herb,
                        'warning': 'Pediatric dosing required - consult healthcare provider'
                    })
                else:
                    recommendations['safe_herbs'].append(herb)
        
        # Comorbidity adjustments
        if patient.has_diabetes and disease != "Diabetes":
            recommendations['warnings'].append({
                'type': 'Comorbidity',
                'message': 'Patient has diabetes - monitor blood glucose closely',
                'action': 'Avoid medications that affect blood sugar'
            })
        
        if patient.has_hypertension and disease != "Hypertension":
            recommendations['warnings'].append({
                'type': 'Comorbidity',
                'message': 'Patient has hypertension - avoid drugs that raise blood pressure',
                'action': 'Monitor blood pressure regularly'
            })
        
        return recommendations
    
    def _get_age_specific_advice(self, age_group: AgeGroup, disease: str) -> List[str]:
        """Get age-appropriate lifestyle advice"""
        advice = []
        
        if age_group == AgeGroup.ELDERLY:
            advice.extend([
                "Start medications at lower doses",
                "Watch for increased side effects",
                "Maintain good hydration",
                "Regular medication review recommended"
            ])
        elif age_group in [AgeGroup.CHILD, AgeGroup.INFANT]:
            advice.extend([
                "Use pediatric formulations only",
                "Dose by weight, not age",
                "Monitor closely for reactions",
                "Keep medications out of reach"
            ])
        elif age_group == AgeGroup.TEEN:
            advice.extend([
                "Follow prescribed dosing carefully",
                "Discuss any concerns with parents/doctor",
                "Maintain healthy lifestyle habits"
            ])
        else:  # Adult
            advice.extend([
                "Follow medication instructions carefully",
                "Maintain healthy diet and exercise",
                "Monitor symptoms and report changes"
            ])
        
        return advice


def format_personalized_output(recommendations: Dict) -> str:
    """Format personalized recommendations for display"""
    output = []
    
    output.append("="*70)
    output.append("PERSONALIZED TREATMENT RECOMMENDATIONS")
    output.append("="*70)
    
    # Patient populations
    if recommendations['patient_populations']:
        output.append(f"\n👤 PATIENT PROFILE:")
        for pop in recommendations['patient_populations']:
            output.append(f"   • {pop.replace('_', ' ').title()}")
    
    # Severity and immediate actions
    if 'severity_message' in recommendations:
        output.append(f"\n{recommendations['severity_message']}")
    
    if recommendations['immediate_actions']:
        output.append(f"\n⚡ IMMEDIATE ACTIONS:")
        for action in recommendations['immediate_actions']:
            output.append(f"   • {action}")
    
    # Warnings
    if recommendations['warnings']:
        output.append(f"\n⚠️  IMPORTANT WARNINGS ({len(recommendations['warnings'])}):")
        for warning in recommendations['warnings'][:5]:
            output.append(f"   • {warning['message']}")
    
    # Contraindications
    if recommendations['contraindications']:
        output.append(f"\n❌ AVOID THESE MEDICATIONS ({len(recommendations['contraindications'])}):")
        for contra in recommendations['contraindications'][:5]:
            output.append(f"   • {contra['drug']}")
            output.append(f"     Reason: {contra['reason']}")
    
    # Dose adjustments
    if recommendations['dose_adjustments']:
        output.append(f"\n📊 SPECIAL CONSIDERATIONS:")
        for adj in recommendations['dose_adjustments'][:5]:
            output.append(f"   • {adj['note']}")
    
    # Safe medications
    if recommendations['safe_drugs']:
        output.append(f"\n✅ SAFE MEDICATION OPTIONS ({len(recommendations['safe_drugs'])}):")
        for drug in recommendations['safe_drugs'][:5]:
            output.append(f"   • {drug.get('name', 'Unknown')}")
    
    # Lifestyle advice
    if recommendations['lifestyle_advice']:
        output.append(f"\n💡 LIFESTYLE ADVICE:")
        for advice in recommendations['lifestyle_advice']:
            output.append(f"   • {advice}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test personalized recommendations
    recommender = PersonalizedRecommender()
    
    print("Testing Personalized Recommendations Engine")
    print("="*70)
    
    # Test Case 1: Pregnant woman with UTI
    print("\n\nTest 1: Pregnant patient with UTI")
    print("-"*70)
    patient1 = PatientProfile(
        age=28,
        gender="female",
        is_pregnant=True
    )
    
    drugs1 = [
        {'name': 'Nitrofurantoin', 'type': 'Antibiotic'},
        {'name': 'Ciprofloxacin', 'type': 'Fluoroquinolone'},
        {'name': 'Trimethoprim-Sulfamethoxazole', 'type': 'Antibiotic'}
    ]
    
    rec1 = recommender.personalize_recommendations(
        disease="Urinary Tract Infection",
        severity_level="Moderate",
        patient=patient1,
        drugs=drugs1
    )
    print(format_personalized_output(rec1))
    
    # Test Case 2: Elderly patient with hypertension
    print("\n\nTest 2: Elderly patient with multiple conditions")
    print("-"*70)
    patient2 = PatientProfile(
        age=72,
        gender="male",
        has_diabetes=True,
        has_hypertension=True
    )
    
    rec2 = recommender.personalize_recommendations(
        disease="Pneumonia",
        severity_level="Severe",
        patient=patient2
    )
    print(format_personalized_output(rec2))
    
    # Test Case 3: Child with fever
    print("\n\nTest 3: Pediatric patient")
    print("-"*70)
    patient3 = PatientProfile(
        age=6,
        gender="female"
    )
    
    drugs3 = [
        {'name': 'Paracetamol', 'type': 'Antipyretic'},
        {'name': 'Aspirin', 'type': 'NSAID'},
        {'name': 'Ibuprofen', 'type': 'NSAID'}
    ]
    
    rec3 = recommender.personalize_recommendations(
        disease="Influenza",
        severity_level="Mild",
        patient=patient3,
        drugs=drugs3
    )
    print(format_personalized_output(rec3))
