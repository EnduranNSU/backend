FILE_PATH = "/opt/airflow/dags/exercise_ingestion/exercises.txt"

from airflow.providers.postgres.hooks.postgres import PostgresHook

def save_to_postgres(exercise: dict[str, str]):
    hook = PostgresHook(postgres_conn_id="postgres")
    engine = hook.get_sqlalchemy_engine()
    with engine.connect() as conn:
        result = conn.execute(
            """
            INSERT INTO exercises (title, tags, hrefs)
            VALUES (%s, %s, %s)
            ON CONFLICT (title) DO NOTHING
            RETURNING id
            """,
            (exercise["title"], [], [])
        )
        inserted = result.fetchone()
    return inserted

    

def delete_from_postgres(exercise: dict[str, str]):
    hook = PostgresHook(postgres_conn_id="postgres")
    conn = hook.get_conn()  
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM exercises
        WHERE title = %s
        RETURNING title
        """,
        (exercise["title"],)
    )

    deleted = cursor.fetchone() is not None
    conn.commit()
    cursor.close()
    conn.close()
    return deleted
