import os
from typing import Optional, Dict, List
import sqlite3
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Handles all database operations for the Student Placement Prediction System.
    Uses SQLite for development and can be extended for PostgreSQL/MySQL.
    """
    
    def __init__(self, db_path: str = "placement_data.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Create database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Execute SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """
        Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            logger.info("Database update successful")
            return True
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Update error: {e}")
            return False
    
    def insert_student_record(self, record: Dict) -> Optional[int]:
        """Insert a full dataset record into the students table."""
        query = """
        INSERT OR REPLACE INTO students (
            student_id, age, gender, branch, college_tier, cgpa,
            internships_count, projects_count, certifications_count,
            coding_skill_score, aptitude_score, communication_skill_score,
            logical_reasoning_score, hackathons_participated, github_repos,
            linkedin_connections, mock_interview_score, attendance_percentage,
            backlogs, extracurricular_score, leadership_score,
            volunteer_experience, sleep_hours, study_hours_per_day,
            placement_status, salary_package_lpa
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            record.get('student_id'),
            record.get('age'),
            record.get('gender'),
            record.get('branch'),
            record.get('college_tier'),
            record.get('cgpa'),
            record.get('internships_count'),
            record.get('projects_count'),
            record.get('certifications_count'),
            record.get('coding_skill_score'),
            record.get('aptitude_score'),
            record.get('communication_skill_score'),
            record.get('logical_reasoning_score'),
            record.get('hackathons_participated'),
            record.get('github_repos'),
            record.get('linkedin_connections'),
            record.get('mock_interview_score'),
            record.get('attendance_percentage'),
            record.get('backlogs'),
            record.get('extracurricular_score'),
            record.get('leadership_score'),
            record.get('volunteer_experience'),
            record.get('sleep_hours'),
            record.get('study_hours_per_day'),
            record.get('placement_status'),
            record.get('salary_package_lpa'),
        )
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error inserting student record: {e}")
            self.connection.rollback()
            return None

    def insert_prediction(self, student_id: int, probability: float, 
                         predicted_placement: str, model_version: str = "1.0") -> Optional[int]:
        """Insert prediction result."""
        query = """
        INSERT INTO placement_predictions 
        (student_id, prediction_probability, predicted_placement, model_version)
        VALUES (?, ?, ?, ?)
        """
        params = (student_id, probability, predicted_placement, model_version)
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error inserting prediction: {e}")
            self.connection.rollback()
            return None

    def get_student_record(self, student_id: int) -> Optional[Dict]:
        """Get a student record by ID."""
        query = "SELECT * FROM students WHERE student_id = ?"
        results = self.execute_query(query, (student_id,))
        return results[0] if results else None

    def get_all_students(self) -> pd.DataFrame:
        """Get all student records as a DataFrame."""
        query = "SELECT * FROM students"
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            logger.error(f"Error fetching students: {e}")
            return pd.DataFrame()

    def get_placement_history(self, student_id: int) -> List[Dict]:
        """Get placement prediction history for a student."""
        query = """
        SELECT * FROM placement_predictions 
        WHERE student_id = ? 
        ORDER BY prediction_date DESC
        """
        return self.execute_query(query, (student_id,))

    def get_model_metrics(self, model_version: str) -> Optional[Dict]:
        """Get metrics for a specific model version."""
        query = "SELECT * FROM model_metrics WHERE model_version = ?"
        results = self.execute_query(query, (model_version,))
        return results[0] if results else None

    def insert_model_metrics(self, model_version: str, accuracy: float, 
                            precision: float, recall: float, f1_score: float,
                            test_samples: int) -> Optional[int]:
        """Insert model performance metrics."""
        query = """
        INSERT INTO model_metrics 
        (model_version, accuracy, precision, recall, f1_score, training_date, test_samples)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (model_version, accuracy, precision, recall, f1_score, 
                 datetime.now(), test_samples)
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error inserting model metrics: {e}")
            self.connection.rollback()
            return None

    def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard."""
        stats = {}
        
        # Total students
        query = "SELECT COUNT(*) as count FROM students"
        result = self.execute_query(query)
        stats['total_students'] = result[0]['count'] if result else 0
        
        # Avg CGPA
        query = "SELECT AVG(cgpa) as avg_cgpa FROM students"
        result = self.execute_query(query)
        stats['avg_cgpa'] = round(result[0]['avg_cgpa'], 2) if result and result[0]['avg_cgpa'] else 0
        
        # Placed students
        query = "SELECT COUNT(*) as count FROM placement_predictions WHERE predicted_placement = 'Placed'"
        result = self.execute_query(query)
        stats['predicted_placed'] = result[0]['count'] if result else 0
        
        # Placement rate
        if stats['total_students'] > 0:
            stats['placement_rate'] = round(
                (stats['predicted_placed'] / stats['total_students']) * 100, 2
            )
        else:
            stats['placement_rate'] = 0
        
        return stats
    
    def initialize_database(self):
        """Initialize database with schema."""
        try:
            with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
                schema = f.read()
            
            cursor = self.connection.cursor()
            cursor.executescript(schema)
            self.connection.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")


# Global database connection
_db_connection = None


def get_db() -> DatabaseConnection:
    """Get database connection instance."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def close_db():
    """Close database connection."""
    global _db_connection
    if _db_connection:
        _db_connection.close()
        _db_connection = None
