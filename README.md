# Student Placement Prediction System

A complete student placement prediction project built with XGBoost, Streamlit, FastAPI, and SQLite.

## Structure

- `frontend/` — Streamlit application for interactive prediction and model reporting.
- `backend/` — XGBoost training, inference pipeline, FastAPI backend, and Supabase integration.
- `database/` — SQLite schema, connection utilities, and dataset loader.
- `student_placement_prediction_dataset_2026 (1).csv` — source dataset for training and evaluation.

## Quick start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Train the model:
   ```bash
   python backend/train_model.py
   ```

3. Run the Streamlit frontend:
   ```bash
   streamlit run frontend/app.py
   ```

4. Run the backend API:
   ```bash
   uvicorn backend.app:app --reload
   ```

## Notes

- The backend includes a FastAPI prediction endpoint at `/predict`.
- The application supports local SQLite storage and optional Supabase prediction logging.
- The dataset loader in `database/data_loader.py` can insert CSV rows into SQLite.
