#!/usr/bin/env python3
"""
Dataset Integration Module
Integrates leftover Kaggle datasets to enhance recommendations
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class DatasetIntegrator:
    """Integrate additional datasets for enhanced recommendations"""
    
    def __init__(self, data_dir: str = "data/kaggle_datasets"):
        self.data_dir = Path(data_dir)
        self.medicinal_plants = None
        self.drug_reviews = None
        self.heart_disease = None
        self.diabetes = None
        self.mental_health = None
        self.liver_disease = None
        self.respiratory = None
        self.covid19 = None
        self.skin_disease = None
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all available datasets"""
        datasets = {}
        
        try:
            self.medicinal_plants = self.load_medicinal_plants()
            if self.medicinal_plants is not None:
                datasets['medicinal_plants'] = self.medicinal_plants
                logger.info(f"✓ Loaded medicinal plants: {len(self.medicinal_plants)} herbs")
        except Exception as e:
            logger.warning(f"Could not load medicinal plants: {e}")
        
        try:
            self.drug_reviews = self.load_drug_reviews()
            if self.drug_reviews is not None:
                datasets['drug_reviews'] = self.drug_reviews
                logger.info(f"✓ Loaded drug reviews: {len(self.drug_reviews)} reviews")
        except Exception as e:
            logger.warning(f"Could not load drug reviews: {e}")
        
        try:
            self.heart_disease = self.load_heart_disease()
            if self.heart_disease is not None:
                datasets['heart_disease'] = self.heart_disease
                logger.info(f"✓ Loaded heart disease data: {len(self.heart_disease)} patients")
        except Exception as e:
            logger.warning(f"Could not load heart disease data: {e}")
        
        try:
            self.diabetes = self.load_diabetes()
            if self.diabetes is not None:
                datasets['diabetes'] = self.diabetes
                logger.info(f"✓ Loaded diabetes data: {len(self.diabetes)} patients")
        except Exception as e:
            logger.warning(f"Could not load diabetes data: {e}")
        
        try:
            self.mental_health = self.load_mental_health()
            if self.mental_health is not None:
                datasets['mental_health'] = self.mental_health
                logger.info(f"✓ Loaded mental health data: {len(self.mental_health)} cases")
        except Exception as e:
            logger.warning(f"Could not load mental health data: {e}")
        
        return datasets
    
    def load_medicinal_plants(self) -> Optional[pd.DataFrame]:
        """Load medicinal plants dataset with effectiveness ratings"""
        path = self.data_dir / "medicinal_plants" / "medicinal_plants.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        # Expected columns: plant_name, medicinal_classification, effectiveness_rating
        return df
    
    def load_drug_reviews(self) -> Optional[pd.DataFrame]:
        """Load drug reviews with effectiveness ratings"""
        path = self.data_dir / "drug_reviews" / "drug_reviews.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        # Expected columns: drug_name, condition, rating, effectiveness
        return df
    
    def load_heart_disease(self) -> Optional[pd.DataFrame]:
        """Load heart disease patient data"""
        path = self.data_dir / "heart_disease" / "heart.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        # Columns: age, sex, cp, trestbps, chol, etc., target (1=disease, 0=healthy)
        return df
    
    def load_diabetes(self) -> Optional[pd.DataFrame]:
        """Load diabetes patient data (Pima Indians dataset)"""
        path = self.data_dir / "diabetes" / "diabetes.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        # Columns: Pregnancies, Glucose, BloodPressure, BMI, Age, Outcome
        return df
    
    def load_mental_health(self) -> Optional[pd.DataFrame]:
        """Load mental health survey data"""
        path = self.data_dir / "mental_health" / "mental_health_data.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        # Columns: anxiety, depression, condition
        return df
    
    def load_liver_disease(self) -> Optional[pd.DataFrame]:
        """Load liver disease patient data"""
        path = self.data_dir / "liver_disease" / "indian_liver_patient.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        return df
    
    def load_respiratory(self) -> Optional[pd.DataFrame]:
        """Load respiratory disease data"""
        path = self.data_dir / "respiratory" / "respiratory_disease.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        return df
    
    def load_covid19(self) -> Optional[pd.DataFrame]:
        """Load COVID-19 data"""
        path = self.data_dir / "covid19" / "covid19_data.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        return df
    
    def load_skin_disease(self) -> Optional[pd.DataFrame]:
        """Load skin disease data"""
        path = self.data_dir / "skin_disease" / "skin_disease_data.csv"
        if not path.exists():
            return None
        
        df = pd.read_csv(path)
        return df
    
    # ==================== ENHANCEMENT METHODS ====================
    
    def get_herb_effectiveness(self, herb_name: str, classification: str = None) -> Optional[float]:
        """Get effectiveness rating for a medicinal plant"""
        if self.medicinal_plants is None:
            return None
        
        # Case-insensitive search
        herb_lower = herb_name.lower()
        matches = self.medicinal_plants[
            self.medicinal_plants['plant_name'].str.lower().str.contains(herb_lower, na=False)
        ]
        
        if matches.empty:
            return None
        
        # If classification specified, filter by it
        if classification:
            class_matches = matches[
                matches['medicinal_classification'].str.lower().str.contains(classification.lower(), na=False)
            ]
            if not class_matches.empty:
                return float(class_matches.iloc[0]['effectiveness_rating'])
        
        # Return first match
        return float(matches.iloc[0]['effectiveness_rating'])
    
    def get_drug_effectiveness(self, drug_name: str, condition: str = None) -> Optional[Dict]:
        """Get average effectiveness and rating for a drug"""
        if self.drug_reviews is None:
            return None
        
        # Case-insensitive search (regex=False to treat as literal string)
        drug_lower = drug_name.lower()
        matches = self.drug_reviews[
            self.drug_reviews['drug_name'].str.lower().str.contains(drug_lower, na=False, regex=False)
        ]
        
        if matches.empty:
            return None
        
        # Filter by condition if specified
        if condition:
            cond_matches = matches[
                matches['condition'].str.lower().str.contains(condition.lower(), na=False)
            ]
            if not cond_matches.empty:
                matches = cond_matches
        
        # Calculate average metrics
        return {
            'average_rating': float(matches['rating'].mean()),
            'average_effectiveness': float(matches['effectiveness'].mean()),
            'review_count': len(matches),
            'condition': condition or 'various'
        }
    
    def get_heart_disease_risk_factors(self) -> Dict:
        """Get common risk factors from heart disease dataset"""
        if self.heart_disease is None:
            return {}
        
        # Patients with heart disease (target=1)
        diseased = self.heart_disease[self.heart_disease['target'] == 1]
        healthy = self.heart_disease[self.heart_disease['target'] == 0]
        
        return {
            'avg_age_diseased': float(diseased['age'].mean()),
            'avg_age_healthy': float(healthy['age'].mean()),
            'avg_cholesterol_diseased': float(diseased['chol'].mean()),
            'avg_cholesterol_healthy': float(healthy['chol'].mean()),
            'avg_bp_diseased': float(diseased['trestbps'].mean()),
            'avg_bp_healthy': float(healthy['trestbps'].mean()),
            'total_patients': len(self.heart_disease),
            'disease_prevalence': float(len(diseased) / len(self.heart_disease))
        }
    
    def get_diabetes_risk_factors(self) -> Dict:
        """Get common risk factors from diabetes dataset"""
        if self.diabetes is None:
            return {}
        
        # Patients with diabetes (Outcome=1)
        diabetic = self.diabetes[self.diabetes['Outcome'] == 1]
        non_diabetic = self.diabetes[self.diabetes['Outcome'] == 0]
        
        return {
            'avg_glucose_diabetic': float(diabetic['Glucose'].mean()),
            'avg_glucose_healthy': float(non_diabetic['Glucose'].mean()),
            'avg_bmi_diabetic': float(diabetic['BMI'].mean()),
            'avg_bmi_healthy': float(non_diabetic['BMI'].mean()),
            'avg_age_diabetic': float(diabetic['Age'].mean()),
            'avg_age_healthy': float(non_diabetic['Age'].mean()),
            'total_patients': len(self.diabetes),
            'diabetes_prevalence': float(len(diabetic) / len(self.diabetes))
        }
    
    def get_mental_health_insights(self) -> Dict:
        """Get mental health condition distribution"""
        if self.mental_health is None:
            return {}
        
        condition_counts = self.mental_health['condition'].value_counts().to_dict()
        
        # Anxiety and depression prevalence
        anxiety_cases = len(self.mental_health[self.mental_health['anxiety'] == 1])
        depression_cases = len(self.mental_health[self.mental_health['depression'] == 1])
        comorbid = len(self.mental_health[
            (self.mental_health['anxiety'] == 1) & (self.mental_health['depression'] == 1)
        ])
        
        return {
            'condition_distribution': condition_counts,
            'anxiety_prevalence': float(anxiety_cases / len(self.mental_health)),
            'depression_prevalence': float(depression_cases / len(self.mental_health)),
            'comorbidity_rate': float(comorbid / len(self.mental_health)),
            'total_cases': len(self.mental_health)
        }
    
    def enhance_herbal_recommendations(self, herbs: List[Tuple[str, float]]) -> List[Dict]:
        """Enhance herbal recommendations with effectiveness ratings"""
        enhanced = []
        
        for herb_name, relevance_score in herbs:
            herb_dict = {
                'name': herb_name,
                'relevance_score': relevance_score
            }
            
            # Try to get effectiveness from medicinal plants dataset
            effectiveness = self.get_herb_effectiveness(herb_name)
            if effectiveness:
                herb_dict['effectiveness_rating'] = effectiveness
                herb_dict['evidence_level'] = 'High' if effectiveness > 0.8 else 'Moderate' if effectiveness > 0.6 else 'Low'
            
            enhanced.append(herb_dict)
        
        return enhanced
    
    def enhance_drug_recommendations(self, drugs: List[Dict]) -> List[Dict]:
        """Enhance drug recommendations with review data"""
        enhanced = []
        
        for drug in drugs:
            drug_copy = drug.copy()
            drug_name = drug.get('name', '')
            
            # Try to get effectiveness from drug reviews
            review_data = self.get_drug_effectiveness(drug_name)
            if review_data:
                drug_copy['user_rating'] = review_data['average_rating']
                drug_copy['user_effectiveness'] = review_data['average_effectiveness']
                drug_copy['review_count'] = review_data['review_count']
            
            enhanced.append(drug_copy)
        
        return enhanced
    
    def get_disease_specific_insights(self, disease: str) -> Dict:
        """Get disease-specific insights from specialized datasets"""
        insights = {}
        disease_lower = disease.lower()
        
        # Heart disease insights
        if any(kw in disease_lower for kw in ['heart', 'cardiac', 'hypertension', 'blood pressure']):
            insights['heart_disease'] = self.get_heart_disease_risk_factors()
        
        # Diabetes insights
        if 'diabetes' in disease_lower or 'blood sugar' in disease_lower:
            insights['diabetes'] = self.get_diabetes_risk_factors()
        
        # Mental health insights
        if any(kw in disease_lower for kw in ['anxiety', 'depression', 'stress', 'mental']):
            insights['mental_health'] = self.get_mental_health_insights()
        
        return insights
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of all loaded datasets"""
        stats = {
            'datasets_loaded': 0,
            'total_records': 0
        }
        
        if self.medicinal_plants is not None:
            stats['medicinal_plants'] = {
                'count': len(self.medicinal_plants),
                'unique_herbs': self.medicinal_plants['plant_name'].nunique(),
                'avg_effectiveness': float(self.medicinal_plants['effectiveness_rating'].mean())
            }
            stats['datasets_loaded'] += 1
            stats['total_records'] += len(self.medicinal_plants)
        
        if self.drug_reviews is not None:
            stats['drug_reviews'] = {
                'count': len(self.drug_reviews),
                'unique_drugs': self.drug_reviews['drug_name'].nunique(),
                'avg_rating': float(self.drug_reviews['rating'].mean()),
                'avg_effectiveness': float(self.drug_reviews['effectiveness'].mean())
            }
            stats['datasets_loaded'] += 1
            stats['total_records'] += len(self.drug_reviews)
        
        if self.heart_disease is not None:
            stats['heart_disease'] = {
                'count': len(self.heart_disease),
                'disease_cases': int((self.heart_disease['target'] == 1).sum()),
                'prevalence': float((self.heart_disease['target'] == 1).mean())
            }
            stats['datasets_loaded'] += 1
            stats['total_records'] += len(self.heart_disease)
        
        if self.diabetes is not None:
            stats['diabetes'] = {
                'count': len(self.diabetes),
                'diabetes_cases': int((self.diabetes['Outcome'] == 1).sum()),
                'prevalence': float((self.diabetes['Outcome'] == 1).mean())
            }
            stats['datasets_loaded'] += 1
            stats['total_records'] += len(self.diabetes)
        
        if self.mental_health is not None:
            stats['mental_health'] = {
                'count': len(self.mental_health),
                'conditions': self.mental_health['condition'].nunique()
            }
            stats['datasets_loaded'] += 1
            stats['total_records'] += len(self.mental_health)
        
        return stats


# Singleton instance for global access
_integrator_instance = None

def get_integrator() -> DatasetIntegrator:
    """Get singleton DatasetIntegrator instance"""
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = DatasetIntegrator()
        try:
            _integrator_instance.load_all_datasets()
        except Exception as e:
            logger.warning(f"Could not load all datasets: {e}")
    return _integrator_instance


if __name__ == "__main__":
    # Test the integrator
    print("=" * 70)
    print("DATASET INTEGRATION TEST")
    print("=" * 70)
    print()
    
    integrator = DatasetIntegrator()
    datasets = integrator.load_all_datasets()
    
    print(f"\n✓ Loaded {len(datasets)} datasets")
    print()
    
    # Test herb effectiveness
    if integrator.medicinal_plants is not None:
        print("Testing herb effectiveness lookup:")
        for herb in ['Tulsi', 'Ashwagandha', 'Turmeric']:
            eff = integrator.get_herb_effectiveness(herb)
            if eff:
                print(f"  {herb}: {eff:.2f}")
    
    # Test drug effectiveness
    if integrator.drug_reviews is not None:
        print("\nTesting drug effectiveness lookup:")
        review = integrator.get_drug_effectiveness('Metformin')
        if review:
            print(f"  Metformin: {review['average_rating']:.2f}/5, {review['average_effectiveness']:.2%} effective")
    
    # Get summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    stats = integrator.get_summary_statistics()
    print(f"\nTotal Datasets Loaded: {stats['datasets_loaded']}")
    print(f"Total Records: {stats['total_records']}")
    print("\nDataset Details:")
    for key, value in stats.items():
        if key not in ['datasets_loaded', 'total_records']:
            print(f"\n{key.upper()}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
