from fastapi import FastAPI

from llm.router import router as llm_router, config


app = FastAPI(title="LLM Proxy")
app.include_router(llm_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "llm",
        "upstream": config.base_url,
        "chat_model": config.chat_model,
        "api_key_configured": bool(config.api_key),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
