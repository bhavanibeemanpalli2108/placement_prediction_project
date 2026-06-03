# Backend Module

This module provides the XGBoost training pipeline and the FastAPI backend for student placement prediction.

## Files

- `model.py` - training, prediction, and persistence for the XGBoost pipeline.
- `train_model.py` - command-line entry point for retraining the model from the dataset.
- `app.py` - FastAPI application exposing prediction and metrics endpoints.
- `supabase_client.py` - optional Supabase integration for logging predictions remotely.
- `requirements.txt` - backend dependency list.

## Run locally

1. Install the backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Train the model:
   ```bash
   python backend/train_model.py
   ```
3. Start the API server:
   ```bash
   uvicorn backend.app:app --reload
   ```

## Endpoints

- `GET /health`
- `GET /metrics`
- `POST /predict`
