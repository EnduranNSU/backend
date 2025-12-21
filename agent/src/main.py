from fastapi import FastAPI

from server import request_router


app = FastAPI(title="Agent Service")
app.include_router(request_router, prefix="/api/v1")
