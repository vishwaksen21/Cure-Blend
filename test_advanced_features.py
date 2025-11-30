"""
Integrated Advanced Features Test Suite

Comprehensive testing for:
1. Multi-disease detection
2. Severity classification
3. Personalized recommendations
4. End-to-end integration
"""

import sys
sys.path.append('/workspaces/Cure-Blend')

from src.multi_disease_detector import MultiDiseaseDetector, format_multi_disease_output
from src.severity_classifier import SeverityClassifier, format_severity_output
from src.personalized_recommender import PersonalizedRecommender, PatientProfile, format_personalized_output

class AdvancedFeaturesTestSuite:
    """Test all advanced features"""
    
    def __init__(self):
        self.detector = MultiDiseaseDetector()
        self.severity_classifier = SeverityClassifier()
        self.recommender = PersonalizedRecommender()
        
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("="*70)
        print("ADVANCED FEATURES TEST SUITE")
        print("="*70)
        
        # Multi-disease detection tests
        print("\n" + "="*70)
        print("TEST CATEGORY 1: MULTI-DISEASE DETECTION")
        print("="*70)
        self.test_single_disease_detection()
        self.test_comorbidity_detection()
        self.test_confidence_thresholds()
        
        # Severity classification tests
        print("\n" + "="*70)
        print("TEST CATEGORY 2: SEVERITY CLASSIFICATION")
        print("="*70)
        self.test_emergency_detection()
        self.test_severe_symptoms()
        self.test_moderate_symptoms()
        self.test_mild_symptoms()
        
        # Personalization tests
        print("\n" + "="*70)
        print("TEST CATEGORY 3: PERSONALIZED RECOMMENDATIONS")
        print("="*70)
        self.test_pregnancy_contraindications()
        self.test_pediatric_adjustments()
        self.test_elderly_considerations()
        self.test_comorbidity_warnings()
        
        # Integration tests
        print("\n" + "="*70)
        print("TEST CATEGORY 4: END-TO-END INTEGRATION")
        print("="*70)
        self.test_complete_workflow()
        
        # Print summary
        self.print_summary()
    
    def assert_test(self, condition, test_name, expected, actual):
        """Assert test result"""
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'PASS',
                'expected': expected,
                'actual': actual
            })
        else:
            print(f"❌ FAIL: {test_name}")
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
            self.tests_failed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'expected': expected,
                'actual': actual
            })
    
    # ===================================
    # Multi-Disease Detection Tests
    # ===================================
    
    def test_single_disease_detection(self):
        """Test clear single disease case"""
        print("\n📋 Test: Single disease detection")
        symptoms = "severe chest pain radiating to left arm"
        result = self.detector.detect_comorbidities(symptoms)
        
        primary = result['primary_disease']['disease']
        has_comorbidities = result['has_multiple_conditions']
        
        self.assert_test(
            primary == "Heart Attack",
            "Single disease - correct diagnosis",
            "Heart Attack",
            primary
        )
        
        self.assert_test(
            not has_comorbidities,
            "Single disease - no comorbidities flagged",
            False,
            has_comorbidities
        )
    
    def test_comorbidity_detection(self):
        """Test multiple disease detection"""
        print("\n📋 Test: Comorbidity detection")
        symptoms = "burning chest pain after eating nausea stomach pain"
        result = self.detector.detect_comorbidities(symptoms)
        
        has_comorbidities = result['has_multiple_conditions']
        num_conditions = 1 + len(result['comorbidities'])
        
        self.assert_test(
            has_comorbidities,
            "Comorbidity - multiple conditions detected",
            True,
            has_comorbidities
        )
        
        self.assert_test(
            num_conditions >= 2,
            "Comorbidity - at least 2 conditions",
            ">=2",
            num_conditions
        )
    
    def test_confidence_thresholds(self):
        """Test confidence threshold filtering"""
        print("\n📋 Test: Confidence thresholds")
        symptoms = "fever headache"
        predictions = self.detector.predict_multiple(symptoms, top_n=5, min_confidence=0.15)
        
        all_above_threshold = all(p['confidence'] >= 0.15 for p in predictions)
        
        self.assert_test(
            all_above_threshold,
            "Confidence - all predictions above threshold",
            True,
            all_above_threshold
        )
    
    # ===================================
    # Severity Classification Tests
    # ===================================
    
    def test_emergency_detection(self):
        """Test emergency severity detection"""
        print("\n📋 Test: Emergency severity detection")
        symptoms = "crushing chest pain cant breathe"
        severity = self.severity_classifier.analyze_severity(symptoms)
        
        self.assert_test(
            severity.level == "Emergency",
            "Emergency - correct severity level",
            "Emergency",
            severity.level
        )
        
        self.assert_test(
            severity.score == 100,
            "Emergency - maximum score",
            100,
            severity.score
        )
        
        self.assert_test(
            severity.urgent,
            "Emergency - urgent flag set",
            True,
            severity.urgent
        )
    
    def test_severe_symptoms(self):
        """Test severe severity detection"""
        print("\n📋 Test: Severe severity detection")
        symptoms = "extreme pain for days getting worse cant eat"
        severity = self.severity_classifier.analyze_severity(symptoms)
        
        self.assert_test(
            severity.level in ["Severe", "Moderate-Severe"],
            "Severe - high severity level",
            "Severe/Moderate-Severe",
            severity.level
        )
        
        self.assert_test(
            severity.score >= 50,
            "Severe - high severity score",
            ">=50",
            severity.score
        )
    
    def test_moderate_symptoms(self):
        """Test moderate severity detection"""
        print("\n📋 Test: Moderate severity detection")
        symptoms = "persistent headache for a week"
        severity = self.severity_classifier.analyze_severity(symptoms)
        
        self.assert_test(
            severity.level in ["Mild", "Moderate"],
            "Moderate - appropriate severity level",
            "Mild/Moderate",
            severity.level
        )
        
        self.assert_test(
            severity.score < 50,
            "Moderate - moderate severity score",
            "<50",
            severity.score
        )
    
    def test_mild_symptoms(self):
        """Test mild severity detection"""
        print("\n📋 Test: Mild severity detection")
        symptoms = "slight runny nose"
        severity = self.severity_classifier.analyze_severity(symptoms)
        
        self.assert_test(
            severity.level == "Mild",
            "Mild - correct severity level",
            "Mild",
            severity.level
        )
        
        self.assert_test(
            not severity.urgent,
            "Mild - not urgent",
            False,
            severity.urgent
        )
    
    # ===================================
    # Personalization Tests
    # ===================================
    
    def test_pregnancy_contraindications(self):
        """Test pregnancy contraindications"""
        print("\n📋 Test: Pregnancy contraindications")
        patient = PatientProfile(age=28, is_pregnant=True)
        
        drugs = [
            {'name': 'Fluoroquinolone'},
            {'name': 'Paracetamol'}
        ]
        
        rec = self.recommender.personalize_recommendations(
            disease="UTI",
            severity_level="Moderate",
            patient=patient,
            drugs=drugs
        )
        
        has_pregnancy_warning = any('pregnant' in str(w).lower() for w in rec['warnings'])
        has_contraindications = len(rec['contraindications']) > 0
        
        self.assert_test(
            has_pregnancy_warning,
            "Pregnancy - warning generated",
            True,
            has_pregnancy_warning
        )
        
        self.assert_test(
            has_contraindications,
            "Pregnancy - contraindications listed",
            True,
            has_contraindications
        )
    
    def test_pediatric_adjustments(self):
        """Test pediatric dosing adjustments"""
        print("\n📋 Test: Pediatric adjustments")
        patient = PatientProfile(age=6)
        
        drugs = [
            {'name': 'Aspirin'},
            {'name': 'Paracetamol'}
        ]
        
        rec = self.recommender.personalize_recommendations(
            disease="Fever",
            severity_level="Mild",
            patient=patient,
            drugs=drugs
        )
        
        has_pediatric_warning = any('children' in str(w).lower() for w in rec['warnings'])
        aspirin_avoided = any('aspirin' in str(d).lower() for d in rec['avoid_drugs'])
        
        self.assert_test(
            has_pediatric_warning,
            "Pediatric - warning generated",
            True,
            has_pediatric_warning
        )
        
        self.assert_test(
            aspirin_avoided,
            "Pediatric - Aspirin contraindicated",
            True,
            aspirin_avoided
        )
    
    def test_elderly_considerations(self):
        """Test elderly patient considerations"""
        print("\n📋 Test: Elderly considerations")
        patient = PatientProfile(age=75)
        
        rec = self.recommender.personalize_recommendations(
            disease="Pneumonia",
            severity_level="Severe",
            patient=patient
        )
        
        has_elderly_warning = any('elderly' in str(w).lower() for w in rec['warnings'])
        has_dose_adjustments = len(rec['dose_adjustments']) > 0
        
        self.assert_test(
            has_elderly_warning,
            "Elderly - warning generated",
            True,
            has_elderly_warning
        )
        
        self.assert_test(
            has_dose_adjustments,
            "Elderly - dose adjustments provided",
            True,
            has_dose_adjustments
        )
    
    def test_comorbidity_warnings(self):
        """Test comorbidity warnings"""
        print("\n📋 Test: Comorbidity warnings")
        patient = PatientProfile(
            age=55,
            has_diabetes=True,
            has_hypertension=True
        )
        
        rec = self.recommender.personalize_recommendations(
            disease="Pneumonia",
            severity_level="Moderate",
            patient=patient
        )
        
        warning_count = len(rec['warnings'])
        has_diabetes_warning = any('diabetes' in str(w).lower() for w in rec['warnings'])
        has_hypertension_warning = any('hypertension' in str(w).lower() for w in rec['warnings'])
        
        self.assert_test(
            warning_count >= 2,
            "Comorbidity - multiple warnings",
            ">=2",
            warning_count
        )
        
        self.assert_test(
            has_diabetes_warning and has_hypertension_warning,
            "Comorbidity - specific condition warnings",
            True,
            has_diabetes_warning and has_hypertension_warning
        )
    
    # ===================================
    # Integration Tests
    # ===================================
    
    def test_complete_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n📋 Test: Complete workflow integration")
        
        # Step 1: Patient presents with symptoms
        symptoms = "severe burning stomach pain after eating for several days"
        patient = PatientProfile(age=45, has_diabetes=True)
        
        # Step 2: Multi-disease detection
        disease_result = self.detector.detect_comorbidities(symptoms)
        primary_disease = disease_result['primary_disease']['disease']
        
        # Step 3: Severity assessment
        severity = self.severity_classifier.analyze_severity(symptoms, primary_disease)
        
        # Step 4: Personalized recommendations
        recommendations = self.recommender.personalize_recommendations(
            disease=primary_disease,
            severity_level=severity.level,
            patient=patient
        )
        
        # Assertions
        workflow_complete = all([
            disease_result is not None,
            primary_disease is not None,
            severity is not None,
            recommendations is not None
        ])
        
        self.assert_test(
            workflow_complete,
            "Integration - all components executed",
            True,
            workflow_complete
        )
        
        has_all_sections = all([
            'warnings' in recommendations,
            'immediate_actions' in recommendations,
            'patient_populations' in recommendations
        ])
        
        self.assert_test(
            has_all_sections,
            "Integration - complete recommendation structure",
            True,
            has_all_sections
        )
        
        print(f"\n   Complete workflow executed:")
        print(f"   ├─ Disease detected: {primary_disease}")
        print(f"   ├─ Severity assessed: {severity.level} ({severity.score}/100)")
        print(f"   ├─ Warnings generated: {len(recommendations['warnings'])}")
        print(f"   └─ Actions recommended: {len(recommendations['immediate_actions'])}")
    
    # ===================================
    # Summary
    # ===================================
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.tests_passed} ✅")
        print(f"   Failed: {self.tests_failed} ❌")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}")
                    print(f"     Expected: {result['expected']}")
                    print(f"     Actual: {result['actual']}")
        
        if pass_rate == 100:
            print(f"\n🎉 ALL TESTS PASSED! Advanced features are working correctly.")
        elif pass_rate >= 90:
            print(f"\n✅ GOOD: Most tests passed. Minor issues to address.")
        elif pass_rate >= 75:
            print(f"\n⚠️ FAIR: Some issues detected. Review failed tests.")
        else:
            print(f"\n❌ POOR: Major issues detected. Significant work needed.")


if __name__ == "__main__":
    suite = AdvancedFeaturesTestSuite()
    suite.run_all_tests()
