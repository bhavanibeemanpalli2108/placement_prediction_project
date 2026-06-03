import os
from typing import Dict, Optional

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://ucxdvmlymgfdtpunbajn.supabase.co",
)
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVjeGR2bWx5bWdmZHRwdW5iYWpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0NzY4ODAsImV4cCI6MjA5NjA1Mjg4MH0.olksPO0Rf-a9lNk7Zwy52vIG6VSvQR8KNx6wKT5IfRg",
)


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_prediction(record: Dict[str, Optional[object]], table_name: str = "placement_predictions") -> Dict[str, object]:
    client = get_supabase_client()
    response = client.table(table_name).insert(record).execute()
    return response.data
