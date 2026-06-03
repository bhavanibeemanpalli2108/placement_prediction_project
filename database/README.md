# Database Module

## Overview

This module handles database operations and schema initialization for the Student Placement Prediction System.
It supports SQLite for local development and can be extended to work with Supabase or other relational databases.

## Files

- `schema.sql` - SQLite-compatible schema for storing student records, predictions, and model metrics.
- `connection.py` - DatabaseConnection class that manages CRUD operations, queries, and schema initialization.
- `data_loader.py` - Utility to load the provided CSV dataset into the local SQLite database.

## Tables

### students
- student_id (Primary Key)
- age, gender, branch, college_tier, cgpa
- internship and project counts
- skill scores and academic indicators
- placement_status and salary_package_lpa

### placement_predictions
- prediction_id (Primary Key)
- student_id
- prediction_probability
- predicted_placement
- model_version
- prediction_date

### model_metrics
- model_id (Primary Key)
- model_version
- accuracy, precision, recall, f1_score
- training_date, test_samples

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the SQLite database:
   ```bash
   python -c "from database.connection import DatabaseConnection; db = DatabaseConnection(); db.initialize_database()"
   ```

3. Load the dataset into SQLite (optional):
   ```bash
   python database/data_loader.py
   ```

## Usage Example

```python
from database.connection import DatabaseConnection

# Initialize the database and insert one student record
conn = DatabaseConnection()
conn.initialize_database()
student_data = {
    "student_id": 1,
    "age": 22,
    "gender": "Male",
    "branch": "CSE",
    "college_tier": "Tier 2",
    "cgpa": 8.2,
    "internships_count": 2,
    "projects_count": 3,
    "certifications_count": 1,
    "coding_skill_score": 72.0,
    "aptitude_score": 66.0,
    "communication_skill_score": 70.0,
    "logical_reasoning_score": 68.0,
    "hackathons_participated": 1,
    "github_repos": 2,
    "linkedin_connections": 150,
    "mock_interview_score": 75.0,
    "attendance_percentage": 85.0,
    "backlogs": 0,
    "extracurricular_score": 55.0,
    "leadership_score": 60.0,
    "volunteer_experience": "Yes",
    "sleep_hours": 7.0,
    "study_hours_per_day": 4.0,
    "placement_status": "Not Placed",
    "salary_package_lpa": 0.0,
}
conn.insert_student_record(student_data)
conn.close()
```
