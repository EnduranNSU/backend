import sys
sys.path.append('/opt/airflow/dags')

from datetime import datetime

from airflow.sdk import dag, task
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

FILE_PATH = "/opt/airflow/dags/exercise_ingestion/exercises.txt"

@dag(start_date=datetime(2024, 1, 1), schedule="@daily", catchup=False)
def exercise_ingestion_pipeline():

    @task
    def get_exercise():
        with open(FILE_PATH) as f:
            return f.readline().strip()

    @task
    def try_insert_postgres(ex_title: str):
        from exercise_ingestion.tasks.postgres import save_to_postgres
        res = save_to_postgres({"title": ex_title})
        print(res)
        if res is None:
            return None
        else:
            return int(res[0])

        
    @task.branch
    def insertion_success(id: int | None):
        if id is not None:
            return "call_llm_agent"
        else:
            return "report_already_created"

    @task
    def call_llm_agent(ex_title: str):
        from exercise_ingestion.tasks.llm_agent_call import llm_agent_call
        return llm_agent_call(ex_title)

    @task
    def clear_llm_reponse(llm_response: str):
        from exercise_ingestion.tasks.clear_md_results import md_to_text
        return md_to_text(llm_response)
    
    @task 
    def save_to_minio(id: int, ex_title: str, clean_llm_response:str):
        from exercise_ingestion.tasks.minio_populator import save_to_minio
        save_to_minio(id, ex_title, clean_llm_response)

    @task
    def save_to_qdrant(id: int, ex_title: str, clean_llm_response: str):
        from exercise_ingestion.tasks.qdrant_populator import save_to_qdrant
        save_to_qdrant(id, ex_title, clean_llm_response)

    @task(trigger_rule=TriggerRule.ONE_FAILED)
    def try_delete_from_postgres(ex_title: str):
        from exercise_ingestion.tasks.postgres import delete_from_postgres
        delete_from_postgres({"title": ex_title})
        print("Rollbacked for exercise {ex_title}...")

    @task
    def success_report(ex_title: str):
        print(f"Ingestion is finished successfully for title: {ex_title}")

    @task
    def report_already_created(ex_title: str):
        print(f"Record for exercise {ex_title} is already created. Skipping...")

    exercise = get_exercise()
    id = try_insert_postgres(exercise)
    branch = insertion_success(id)
    report_created = report_already_created(exercise)

    llm_call = call_llm_agent(exercise)
    clean_llm_response = clear_llm_reponse(llm_call)

    delete = try_delete_from_postgres(exercise)
    ingest_minio = save_to_minio(id, exercise, clean_llm_response)
    ingest_qdrant = save_to_qdrant(id, exercise, clean_llm_response)


    successed_report = success_report(exercise)

    branch >> llm_call >> clean_llm_response >> [ingest_minio, ingest_qdrant] >> successed_report
    branch >> report_created
    [llm_call, clean_llm_response, ingest_minio, ingest_qdrant] >> delete

dag = exercise_ingestion_pipeline() 
