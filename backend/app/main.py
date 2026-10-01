from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app import models  # noqa: F401
from app.config import get_settings
from app.database import create_engine_from_settings, init_db
from app.dependencies import limiter
from app.logging_config import setup_logging
from app.middleware import RequestIDMiddleware
from app.routers import commissions, dashboard, transactions

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine = create_engine_from_settings(settings)
    app.state.engine = engine
    init_db(engine)
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(title="Freelance Artist Finance", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestIDMiddleware)
settings = get_settings()
cors_origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(commissions.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/detailed")
def health_detailed(request: Request):
    settings = get_settings()
    # DB ping
    db_ok = False
    try:
        engine = request.app.state.engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # LLM reachable flag
    llm_reachable = False
    if settings.llm_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                timeout=2.0,
                max_retries=0,
            )
            # Lightweight probe - list models with short timeout
            client.models.list()
            llm_reachable = True
        except Exception:
            llm_reachable = False

    return {
        "status": "ok" if db_ok else "degraded",
        "db_ping": db_ok,
        "llm_reachable": llm_reachable,
    }
