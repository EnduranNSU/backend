from fastapi import FastAPI

from cv_service.routers import cv_router, cv_ws_router


app = FastAPI(title="CV Service")
app.include_router(cv_router)
app.include_router(cv_ws_router)


@app.get("/")
def root():
    return {"status": "ok", "service": "cv_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9090)
