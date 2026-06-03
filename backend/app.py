import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.model import PlacementModel
from backend.supabase_client import insert_prediction

app = FastAPI(
    title="Student Placement Prediction API",
    description="Backend API for XGBoost-based student placement predictions.",
    version="1.0.0",
)

model = PlacementModel()
try:
    model.load()
except FileNotFoundError:
    model = PlacementModel()


class PredictionRequest(BaseModel):
    student_id: int = Field(..., example=101)
    age: int = Field(..., example=22)
    gender: str = Field(..., example="Male")
    cgpa: float = Field(..., example=8.2)
    branch: str = Field(..., example="CSE")
    college_tier: str = Field(..., example="Tier 2")
    internships_count: int = Field(..., example=2)
    projects_count: int = Field(..., example=4)
    certifications_count: int = Field(..., example=3)
    coding_skill_score: float = Field(..., example=72.0)
    aptitude_score: float = Field(..., example=65.0)
    communication_skill_score: float = Field(..., example=70.0)
    logical_reasoning_score: float = Field(..., example=68.0)
    hackathons_participated: int = Field(..., example=1)
    github_repos: int = Field(..., example=2)
    linkedin_connections: int = Field(..., example=150)
    mock_interview_score: float = Field(..., example=75.0)
    attendance_percentage: float = Field(..., example=85.0)
    backlogs: int = Field(..., example=0)
    extracurricular_score: float = Field(..., example=60.0)
    leadership_score: float = Field(..., example=55.0)
    volunteer_experience: str = Field(..., example="Yes")
    sleep_hours: float = Field(..., example=7.0)
    study_hours_per_day: float = Field(..., example=4.0)


class PredictionResponse(BaseModel):
    student_id: int
    predicted_placement: str
    placement_probability: float
    threshold: float


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "model_loaded": model.pipeline is not None}


@app.get("/metrics")
def metrics() -> dict:
    try:
        return model.get_metrics()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model is not trained yet. Run backend/train_model.py to generate the model.")


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> dict:
    if model.pipeline is None:
        raise HTTPException(status_code=503, detail="Model is not trained yet. Run backend/train_model.py to generate the model.")

    features = payload.dict()
    student_id = features.pop("student_id")
    prediction = model.predict(features)
    saved_record = {
        "student_id": student_id,
        **features,
        "predicted_placement": prediction["predicted_placement"],
        "placement_probability": prediction["placement_probability"],
    }
    try:
        insert_prediction(saved_record)
    except Exception:
        pass
    return {
        "student_id": student_id,
        **prediction,
    }
