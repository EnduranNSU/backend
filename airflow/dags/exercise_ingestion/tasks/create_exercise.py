FILE_PATH = "/opt/airflow/dags/exercise_ingestion/exercises.txt"

from airflow.providers.postgres.hooks.postgres import PostgresHook

def create_exercise(text: str):
    hook = PostgresHook(postgres_conn_id="postgres")
    engine = hook.get_sqlalchemy_engine()
    with engine.connect() as conn:
        conn.execute(
            """
            INSERT INTO exercises (text)
            VALUES (:text)
            ON CONFLICT (text) DO NOTHING
            """,
            {"text": text}
        )
    