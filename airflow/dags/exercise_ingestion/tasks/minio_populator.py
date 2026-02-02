import io

from minio import Minio
from airflow.hooks.base import BaseHook

def save_to_minio(id: int, ex_title: str, clean_llm_response:str):
    conn = BaseHook.get_connection("minio")
    extra = conn.extra_dejson
    client = Minio(f"{extra['host']}:{extra['port']}", access_key=extra['login'], secret_key=extra['password'], secure=False)
    bucket = 'exercises'

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    obj_name = f"ex-{id}.txt"
    data = clean_llm_response.encode('utf-8')
    data_stream = io.BytesIO(data)
    client.put_object(
        bucket,
        obj_name,
        data_stream,
        length = len(data),
        content_type="text/plain"
    )
