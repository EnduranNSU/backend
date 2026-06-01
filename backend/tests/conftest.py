"""
Set up test environment BEFORE any backend code is imported.
We replace:
  - session.py  →  in-memory SQLite async engine
  - config      →  a minimal mock so get_config() never reads files
"""
import os, sys, json
from unittest.mock import MagicMock
from pathlib import Path

# ── 1. Point DB_URL to SQLite so session.py doesn't need psycopg ──────────
os.environ.setdefault("DB_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("AUTH_SECRET_KEY", "test-secret-key")
os.environ.setdefault("MINIO_ROOT_USER", "minioadmin")
os.environ.setdefault("MINIO_ROOT_PASSWORD", "minioadmin")

# ── 2. Mock config before it tries to read config.json ───────────────────
mock_cfg = MagicMock()
mock_cfg.authentication.secret_key = "test-secret-key"
mock_cfg.authentication.algorithm = "HS256"
mock_cfg.authentication.access_token_expiration_minutes = 30

import backend.config as _backend_config
_backend_config._config = mock_cfg

# ── 3. Fixtures ───────────────────────────────────────────────────────────
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import TypeDecorator, Text

# SQLite-compatible ARRAY replacement
class JSONArray(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        import json as _json
        return _json.dumps(value or [])

    def process_result_value(self, value, dialect):
        import json as _json
        if not value:
            return []
        return _json.loads(value)

# Patch postgresql.ARRAY globally
import sqlalchemy.dialects.postgresql as _pg
_pg.ARRAY = lambda *a, **kw: JSONArray()

from backend.database.sqlalchemy.orm_models import Base


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
