"""
User Feedback System

Collects and stores user feedback on predictions to enable:
- Continuous model improvement
- Accuracy tracking in production
- Identification of weak areas
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

class FeedbackSystem:
    """Manage user feedback on predictions"""
    
    def __init__(self, db_path: str = "data/feedback.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create feedback database if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                predicted_disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                rating INTEGER,
                helpful BOOLEAN,
                actual_diagnosis TEXT,
                comments TEXT,
                user_id TEXT,
                session_id TEXT
            )
        """)
        
        # Analytics table for aggregated stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disease_stats (
                disease TEXT PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                helpful_count INTEGER DEFAULT 0,
                unhelpful_count INTEGER DEFAULT 0,
                avg_confidence REAL,
                last_updated TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_feedback(
        self,
        symptoms: str,
        predicted_disease: str,
        confidence: float,
        helpful: Optional[bool] = None,
        rating: Optional[int] = None,
        actual_diagnosis: Optional[str] = None,
        comments: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        """
        Record user feedback on a prediction
        
        Args:
            symptoms: User's input symptoms
            predicted_disease: What the model predicted
            confidence: Model's confidence score
            helpful: Whether prediction was helpful (True/False)
            rating: 1-5 star rating (optional)
            actual_diagnosis: What doctor actually diagnosed (optional)
            comments: Free-text feedback (optional)
            user_id: Anonymous user identifier (optional)
            session_id: Session identifier (optional)
            
        Returns:
            Feedback entry ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback (
                timestamp, symptoms, predicted_disease, confidence,
                rating, helpful, actual_diagnosis, comments,
                user_id, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            symptoms,
            predicted_disease,
            confidence,
            rating,
            helpful,
            actual_diagnosis,
            comments,
            user_id,
            session_id
        ))
        
        feedback_id = cursor.lastrowid
        
        # Update disease stats
        self._update_disease_stats(cursor, predicted_disease, confidence, helpful)
        
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def _update_disease_stats(self, cursor, disease: str, confidence: float, helpful: Optional[bool]):
        """Update aggregated disease statistics"""
        cursor.execute("""
            INSERT INTO disease_stats (disease, total_predictions, helpful_count, unhelpful_count, avg_confidence, last_updated)
            VALUES (?, 1, ?, ?, ?, ?)
            ON CONFLICT(disease) DO UPDATE SET
                total_predictions = total_predictions + 1,
                helpful_count = helpful_count + ?,
                unhelpful_count = unhelpful_count + ?,
                avg_confidence = ((avg_confidence * total_predictions) + ?) / (total_predictions + 1),
                last_updated = ?
        """, (
            disease,
            1 if helpful is True else 0,
            1 if helpful is False else 0,
            confidence,
            datetime.now().isoformat(),
            1 if helpful is True else 0,
            1 if helpful is False else 0,
            confidence,
            datetime.now().isoformat()
        ))
    
    def get_disease_performance(self, disease: str) -> Optional[Dict]:
        """Get performance metrics for a specific disease"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT total_predictions, helpful_count, unhelpful_count, 
                   avg_confidence, last_updated
            FROM disease_stats
            WHERE disease = ?
        """, (disease,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        total, helpful, unhelpful, avg_conf, updated = row
        helpful_rate = helpful / total if total > 0 else 0
        
        return {
            'disease': disease,
            'total_predictions': total,
            'helpful_count': helpful,
            'unhelpful_count': unhelpful,
            'helpful_rate': helpful_rate,
            'avg_confidence': avg_conf,
            'last_updated': updated
        }
    
    def get_low_performing_diseases(self, min_predictions: int = 10, helpful_threshold: float = 0.7) -> List[Dict]:
        """Identify diseases with low helpful rates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT disease, total_predictions, helpful_count, unhelpful_count, avg_confidence
            FROM disease_stats
            WHERE total_predictions >= ?
            ORDER BY (CAST(helpful_count AS REAL) / total_predictions) ASC
            LIMIT 20
        """, (min_predictions,))
        
        results = []
        for row in cursor.fetchall():
            disease, total, helpful, unhelpful, avg_conf = row
            helpful_rate = helpful / total if total > 0 else 0
            
            if helpful_rate < helpful_threshold:
                results.append({
                    'disease': disease,
                    'total_predictions': total,
                    'helpful_rate': helpful_rate,
                    'avg_confidence': avg_conf,
                    'needs_improvement': True
                })
        
        conn.close()
        return results
    
    def get_mislabeled_cases(self, limit: int = 50) -> List[Dict]:
        """Get cases where actual diagnosis differs from prediction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symptoms, predicted_disease, actual_diagnosis, confidence, timestamp
            FROM feedback
            WHERE actual_diagnosis IS NOT NULL 
              AND actual_diagnosis != predicted_disease
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'symptoms': row[0],
                'predicted': row[1],
                'actual': row[2],
                'confidence': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        return results
    
    def export_training_corrections(self, output_path: str):
        """Export mislabeled cases for model retraining"""
        cases = self.get_mislabeled_cases(limit=1000)
        
        import pandas as pd
        df = pd.DataFrame(cases)
        
        # Create corrected training data
        corrected = pd.DataFrame({
            'symptom_text': df['symptoms'],
            'disease': df['actual'],
            'source': 'user_correction',
            'confidence': 1.0  # High confidence since diagnosed by doctor
        })
        
        corrected.to_csv(output_path, index=False)
        print(f"Exported {len(corrected)} corrections to {output_path}")
        
        return corrected
    
    def get_summary_stats(self) -> Dict:
        """Get overall feedback statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total feedback
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]
        
        # Helpful rate
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE helpful = 1")
        helpful = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE helpful = 0")
        unhelpful = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]
        
        # Corrections received
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE actual_diagnosis IS NOT NULL")
        corrections = cursor.fetchone()[0]
        
        conn.close()
        
        helpful_rate = helpful / (helpful + unhelpful) if (helpful + unhelpful) > 0 else 0
        
        return {
            'total_feedback': total_feedback,
            'helpful_count': helpful,
            'unhelpful_count': unhelpful,
            'helpful_rate': helpful_rate,
            'avg_rating': avg_rating,
            'corrections_received': corrections,
            'accuracy_estimate': helpful_rate  # Proxy for accuracy
        }


def display_feedback_prompt() -> str:
    """Generate user-friendly feedback prompt"""
    return """
### 📊 Help Us Improve!

Was this prediction helpful?

Your feedback helps improve the system for everyone.
"""

def display_detailed_feedback_form() -> str:
    """Generate detailed feedback form"""
    return """
### 💬 Optional: Tell Us More

- **What did your doctor diagnose?** (helps us learn from mistakes)
- **How accurate was this prediction?** (1-5 stars)
- **Any additional comments?**
"""


if __name__ == "__main__":
    # Example usage
    feedback = FeedbackSystem()
    
    # Simulate some feedback
    feedback.record_feedback(
        symptoms="fever headache body aches",
        predicted_disease="Influenza",
        confidence=0.85,
        helpful=True,
        rating=5
    )
    
    feedback.record_feedback(
        symptoms="chest pain difficulty breathing",
        predicted_disease="Asthma",
        confidence=0.65,
        helpful=False,
        actual_diagnosis="Heart Attack",
        comments="This was very dangerous! System missed critical symptoms."
    )
    
    # Get stats
    print("Summary Statistics:")
    stats = feedback.get_summary_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nLow Performing Diseases:")
    low_perf = feedback.get_low_performing_diseases(min_predictions=1)
    for disease in low_perf:
        print(f"  {disease['disease']}: {disease['helpful_rate']:.1%} helpful")
