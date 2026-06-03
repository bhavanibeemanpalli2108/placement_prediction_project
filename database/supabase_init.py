import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()


def load_sql_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def init_supabase_schema() -> None:
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise EnvironmentError(
            "Please set SUPABASE_DB_URL in your environment to the Supabase database URL."
        )

    schema_path = Path(__file__).resolve().parent / "supabase_schema.sql"
    schema_sql = load_sql_file(schema_path)

    with psycopg2.connect(db_url) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            print("Supabase schema created or verified successfully.")


if __name__ == "__main__":
    init_supabase_schema()
