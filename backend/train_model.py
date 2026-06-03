import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.model import PlacementModel


def main() -> None:
    dataset_path = ROOT_DIR / "student_placement_prediction_dataset_2026 (1).csv"
    model = PlacementModel()
    metrics = model.fit(str(dataset_path), test_size=0.2)
    print("Trained XGBoost model successfully")
    print(f"Accuracy: {metrics.accuracy:.4f}")
    print(f"Precision: {metrics.precision:.4f}")
    print(f"Recall: {metrics.recall:.4f}")
    print(f"F1 Score: {metrics.f1_score:.4f}")


if __name__ == "__main__":
    main()
