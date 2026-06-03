import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st

from backend.model import PlacementModel, load_dataset_preview

MODEL_INFO_PATH = Path(__file__).resolve().parent.parent / "backend" / "model" / "model_metrics.json"


@st.cache_data
def load_model() -> PlacementModel:
    model = PlacementModel()
    try:
        model.load()
    except FileNotFoundError:
        return model
    return model


@st.cache_data
def load_preview() -> pd.DataFrame:
    preview = load_dataset_preview(Path(__file__).resolve().parent.parent / "student_placement_prediction_dataset_2026 (1).csv", n=5)
    return pd.DataFrame(preview)


def draw_input_form() -> Dict[str, Any]:
    st.sidebar.header("Enter student features")

    profile = {
        "age": st.sidebar.number_input("Age", min_value=17, max_value=35, value=22),
        "gender": st.sidebar.selectbox("Gender", ["Male", "Female", "Other"]),
        "cgpa": st.sidebar.slider("CGPA", 0.0, 10.0, 7.5, 0.01),
        "branch": st.sidebar.selectbox("Branch", ["CSE", "IT", "EEE", "ECE", "MECH", "CIVIL", "BIO"]),
        "college_tier": st.sidebar.selectbox("College Tier", ["Tier 1", "Tier 2", "Tier 3"]),
        "internships_count": st.sidebar.number_input("Internships", min_value=0, max_value=10, value=1),
        "projects_count": st.sidebar.number_input("Projects", min_value=0, max_value=10, value=3),
        "certifications_count": st.sidebar.number_input("Certifications", min_value=0, max_value=10, value=2),
        "coding_skill_score": st.sidebar.slider("Coding Skill Score", 0.0, 100.0, 70.0, 0.1),
        "aptitude_score": st.sidebar.slider("Aptitude Score", 0.0, 100.0, 65.0, 0.1),
        "communication_skill_score": st.sidebar.slider("Communication Score", 0.0, 100.0, 70.0, 0.1),
        "logical_reasoning_score": st.sidebar.slider("Logical Reasoning Score", 0.0, 100.0, 70.0, 0.1),
        "hackathons_participated": st.sidebar.number_input("Hackathons", min_value=0, max_value=10, value=0),
        "github_repos": st.sidebar.number_input("GitHub Repos", min_value=0, max_value=30, value=2),
        "linkedin_connections": st.sidebar.number_input("LinkedIn Connections", min_value=0, max_value=2000, value=120),
        "mock_interview_score": st.sidebar.slider("Mock Interview Score", 0.0, 100.0, 68.0, 0.1),
        "attendance_percentage": st.sidebar.slider("Attendance %", 0.0, 100.0, 85.0, 0.1),
        "backlogs": st.sidebar.number_input("Backlogs", min_value=0, max_value=10, value=0),
        "extracurricular_score": st.sidebar.slider("Extracurricular Score", 0.0, 100.0, 55.0, 0.1),
        "leadership_score": st.sidebar.slider("Leadership Score", 0.0, 100.0, 55.0, 0.1),
        "volunteer_experience": st.sidebar.selectbox("Volunteer Experience", ["Yes", "No"]),
        "sleep_hours": st.sidebar.slider("Sleep Hours", 0.0, 12.0, 7.0, 0.1),
        "study_hours_per_day": st.sidebar.slider("Study Hours per Day", 0.0, 12.0, 5.0, 0.1),
    }
    return profile


def main():
    st.set_page_config(
        page_title="Student Placement Predictor",
        page_icon="🎓",
        layout="wide",
    )

    st.title("Student Placement Prediction System")
    st.markdown(
        "Use the sidebar to enter student metrics and predict placement probability with an XGBoost model."
    )

    model = load_model()
    try:
        metrics = model.get_metrics()
        st.subheader("Model performance")
        st.metric("Accuracy", metrics.get("accuracy", "N/A"))
        col1, col2, col3 = st.columns(3)
        col1.metric("Precision", metrics.get("precision", "N/A"))
        col2.metric("Recall", metrics.get("recall", "N/A"))
        col3.metric("F1 Score", metrics.get("f1_score", "N/A"))
    except FileNotFoundError:
        st.warning("Model file not found. Train the model with `python backend/train_model.py` before predicting.")
        metrics = {}

    st.subheader("Sample dataset preview")
    st.dataframe(load_preview())

    st.subheader("Predict placement")
    profile = draw_input_form()
    if st.button("Run prediction"):
        prediction = model.predict(profile)
        st.success(f"Predicted placement: {prediction['predicted_placement']}")
        st.info(f"Placement probability: {prediction['placement_probability'] * 100:.2f}%")
        st.write("---")
        st.json(prediction)
        if prediction["predicted_placement"] == "Placed":
            st.balloons()

    st.sidebar.markdown("---")
    st.sidebar.write("Streamlit app powered by XGBoost and scikit-learn.")


if __name__ == "__main__":
    main()
