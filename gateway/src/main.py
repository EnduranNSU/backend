import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gateway.proxy import router as proxy_router, ROUTES
from gateway.ws_proxy import router as ws_router
from gateway import openapi as openapi_agg


app = FastAPI(
    title="Gateway",
    description="Единая точка входа: backend / cv / retriever / agent / llm",
)


# CORS — позволяет браузерному фронту (vite на 5173, next на 3000 и т.д.)
# дёргать gateway. CORS_ALLOW_ORIGINS можно перепутать в .env через запятую.
_cors_env = os.environ.get("CORS_ALLOW_ORIGINS", "*")
_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=None if _origins != ["*"] else ".*",
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return {
        "status": "ok",
        "service": "gateway",
        "docs": "/docs",
        "routes": [{"prefix": p, "upstream": u} for p, u, _ in ROUTES],
    }


@app.post("/_admin/openapi/refresh", include_in_schema=False)
def refresh_openapi():
    """Drop the aggregated openapi cache (call after restarting an upstream)."""
    openapi_agg.invalidate()
    return {"status": "ok"}


# Replace FastAPI's auto-generated openapi with one merged from upstream services.
app.openapi = openapi_agg.build  # type: ignore[assignment]


# WebSocket routes must be registered BEFORE the catch-all HTTP proxy.
app.include_router(ws_router)

# Catch-all proxy must be registered last so concrete routes above win.
app.include_router(proxy_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
