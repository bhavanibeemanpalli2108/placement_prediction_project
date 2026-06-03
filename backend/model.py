import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

ROOT_DIR = Path(__file__).resolve().parent
MODEL_DIR = ROOT_DIR / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "xgb_pipeline.joblib"
METRICS_PATH = MODEL_DIR / "model_metrics.json"

NUMERIC_FEATURES = [
    "age",
    "cgpa",
    "internships_count",
    "projects_count",
    "certifications_count",
    "coding_skill_score",
    "aptitude_score",
    "communication_skill_score",
    "logical_reasoning_score",
    "hackathons_participated",
    "github_repos",
    "linkedin_connections",
    "mock_interview_score",
    "attendance_percentage",
    "backlogs",
    "extracurricular_score",
    "leadership_score",
    "sleep_hours",
    "study_hours_per_day",
    "volunteer_experience",
]
CATEGORICAL_FEATURES = ["gender", "branch", "college_tier"]
TARGET_COLUMN = "placement_status"
VALID_LABELS = ["Placed", "Not Placed"]


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "volunteer_experience" in df.columns:
        df["volunteer_experience"] = df["volunteer_experience"].map(
            {"Yes": 1, "yes": 1, "Y": 1, "No": 0, "no": 0, "N": 0}
        ).fillna(0).astype(int)

    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df[CATEGORICAL_FEATURES] = df[CATEGORICAL_FEATURES].astype(str).fillna("Unknown")
    return df


def _build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[("scaler", StandardScaler())]
    )
    categorical_transformer = Pipeline(
        steps=[
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    classifier = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        n_estimators=200,
        learning_rate=0.08,
        max_depth=5,
        subsample=0.8,
        random_state=42,
        tree_method="hist",
    )

    pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", classifier)]
    )
    return pipeline


def _encode_target(series: pd.Series) -> np.ndarray:
    return series.map(lambda x: 1 if str(x).strip().lower() == "placed" else 0).astype(int).to_numpy()


@dataclass
class ModelMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    support: int
    test_size: float
    params: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "support": int(self.support),
            "test_size": self.test_size,
            "params": self.params,
        }


class PlacementModel:
    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.metrics: Optional[ModelMetrics] = None

    def fit(self, csv_path: str, test_size: float = 0.2, random_state: int = 42) -> ModelMetrics:
        df = pd.read_csv(csv_path)
        df = _normalize_dataframe(df)

        X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
        y = _encode_target(df[TARGET_COLUMN])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, stratify=y, random_state=random_state
        )

        self.pipeline = _build_pipeline()
        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        self.metrics = ModelMetrics(
            accuracy=accuracy_score(y_test, y_pred),
            precision=precision_score(y_test, y_pred, zero_division=0),
            recall=recall_score(y_test, y_pred, zero_division=0),
            f1_score=f1_score(y_test, y_pred, zero_division=0),
            support=len(y_test),
            test_size=test_size,
            params=self.pipeline[-1].get_params(),
        )

        self.save()
        self.save_metrics()
        return self.metrics

    def save(self) -> None:
        if self.pipeline is None:
            raise RuntimeError("Cannot save model because it is not trained yet.")
        joblib.dump(self.pipeline, MODEL_PATH)

    def save_metrics(self) -> None:
        if self.metrics is None:
            raise RuntimeError("Cannot save metrics because they are not available.")
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metrics.to_json(), f, indent=2)

    def load(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        self.pipeline = joblib.load(MODEL_PATH)
        if METRICS_PATH.exists():
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
                self.metrics = ModelMetrics(
                    accuracy=metrics_data["accuracy"],
                    precision=metrics_data["precision"],
                    recall=metrics_data["recall"],
                    f1_score=metrics_data["f1_score"],
                    support=metrics_data["support"],
                    test_size=metrics_data["test_size"],
                    params=metrics_data.get("params", {}),
                )

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.pipeline is None:
            self.load()

        raw = pd.DataFrame([payload])
        raw = _normalize_dataframe(raw)
        X = raw[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        probability = float(self.pipeline.predict_proba(X)[:, 1][0])
        label = "Placed" if probability >= 0.5 else "Not Placed"
        return {
            "placement_probability": round(probability, 4),
            "predicted_placement": label,
            "threshold": 0.5,
        }

    def get_metrics(self) -> Dict[str, Any]:
        if self.metrics is None:
            self.load()
        return self.metrics.to_json() if self.metrics else {}


def load_dataset_preview(csv_path: str, n: int = 5) -> List[Dict[str, Any]]:
    df = pd.read_csv(csv_path)
    return df.head(n).to_dict(orient="records")
