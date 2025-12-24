from fastapi import FastAPI

from agent.routers import agent_router

app = FastAPI(title="Agent Service")
app.include_router(agent_router)

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)
