-- Supabase (PostgreSQL) schema for Student Placement Prediction System

CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    age INTEGER,
    gender TEXT,
    branch TEXT,
    college_tier TEXT,
    cgpa REAL,
    internships_count INTEGER,
    projects_count INTEGER,
    certifications_count INTEGER,
    coding_skill_score REAL,
    aptitude_score REAL,
    communication_skill_score REAL,
    logical_reasoning_score REAL,
    hackathons_participated INTEGER,
    github_repos INTEGER,
    linkedin_connections INTEGER,
    mock_interview_score REAL,
    attendance_percentage REAL,
    backlogs INTEGER,
    extracurricular_score REAL,
    leadership_score REAL,
    volunteer_experience TEXT,
    sleep_hours REAL,
    study_hours_per_day REAL,
    placement_status TEXT,
    salary_package_lpa REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS placement_predictions (
    prediction_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id) ON DELETE CASCADE,
    prediction_probability REAL,
    predicted_placement TEXT,
    model_version TEXT,
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_metrics (
    model_id SERIAL PRIMARY KEY,
    model_version TEXT,
    accuracy REAL,
    precision REAL,
    recall REAL,
    f1_score REAL,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    test_samples INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_students_branch ON students(branch);
CREATE INDEX IF NOT EXISTS idx_students_college_tier ON students(college_tier);
CREATE INDEX IF NOT EXISTS idx_predictions_student_id ON placement_predictions(student_id);
CREATE INDEX IF NOT EXISTS idx_metrics_model_version ON model_metrics(model_version);
