from fastapi import FastAPI
from retriever.routers import ExerciseRouter, UserRouter


app = FastAPI(title="Retriever Service")

app.include_router(ExerciseRouter)
app.include_router(UserRouter)


@app.get("/")
def root():
    return {"status": "ok", "service": "retriever"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
