# Хз, это написала гптшка. Вроде все должно правильно работать
# Общий принцип. Не лезть в __init__ и get_instance. Они нужны, чтобы правильно работал синглтон
# Изначально S3Client инится в main.py, потом на нем просто вызывается get_instance и больше ничего трогать не надо
# Методы download_execution и download_chatbot на момент написания этого текста нигде не используются. 
# Скорее всего, есть смысл переделать их на работу не с байтами, а на работу объектами Chatbot и Execution, чтобы полностью изолировать этот кусок 
import io

from minio import Minio
from typing import Optional
import threading


class S3Client:
    _instance: Optional["S3Client"] = None
    _lock = threading.Lock()

    _instance = None

    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        self.bucket = "exercises"
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        S3Client._instance = self
        print("S3Client initialized")

    @staticmethod
    def get_instance() -> "S3Client":
        if S3Client._instance is None:
            raise RuntimeError("S3Client not initialized yet. Expected call of constructor beforehand.")
        return S3Client._instance


    def upload(self, obj_name: str, data: bytes):
        data_stream = io.BytesIO(data)

        self.client.put_object(
            self.bucket,
            obj_name,
            data_stream,
            length=len(data),
            content_type="text/plain",
        )

    def download(self, obj_name: str) -> bytes:
        response = self.client.get_object(self.bucket, obj_name)
        return response.read()
    

    def upload_exercise_description(self, exercise_id: int, description: str):
        obj_name = f"ex-{exercise_id}.txt"
        self.upload(obj_name, description.encode("utf-8"))

    def download_exercise_description(self, exercise_id: int) -> str:
        obj_name = f"ex-{exercise_id}.txt"
        description = self.download(obj_name)
        return description.decode("utf-8")
    