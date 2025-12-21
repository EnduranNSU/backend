from fastapi import FastAPI
from retriever.routers import search

app = FastAPI(title="Retriever Service")

app.include_router(search.router, prefix="/search", tags=["search"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Retriever is alive"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
