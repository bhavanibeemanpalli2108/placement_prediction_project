import pandas as pd
from pathlib import Path

from database.connection import DatabaseConnection


def load_dataset_to_sqlite(csv_path: str, db_path: str = "placement_data.db", limit: int | None = None) -> int:
    df = pd.read_csv(csv_path)
    if limit is not None:
        df = df.head(limit)

    db = DatabaseConnection(db_path)
    db.initialize_database()

    inserted = 0
    for record in df.to_dict(orient="records"):
        success = db.insert_student_record(record)
        if success:
            inserted += 1
    db.close()
    return inserted


if __name__ == "__main__":
    path = Path(__file__).resolve().parent.parent / "student_placement_prediction_dataset_2026 (1).csv"
    count = load_dataset_to_sqlite(str(path))
    print(f"Inserted {count} records into SQLite database.")
