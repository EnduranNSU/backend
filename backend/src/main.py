from fastapi import FastAPI

from backend.minio.S3Client import S3Client
from backend.routers import access_router, user_router, exercise_router, measurement_router, training_router
from backend.config import get_config

config = get_config()
endpoint = "{}:{}".format(config.s3.host, config.s3.port)
S3Client(endpoint, config.s3.user, config.s3.password)  

server = FastAPI()

server.include_router(user_router)
server.include_router(access_router)
server.include_router(exercise_router)
server.include_router(measurement_router)
server.include_router(training_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server, host="0.0.0.0", port=8080)
