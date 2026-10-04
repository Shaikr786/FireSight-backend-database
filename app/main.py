from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import matches

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "service": "firesight-api"}


@app.get("/")
def root():
    return {
        "message": "FireSight Sports API",
        "docs": "/docs",
        "health": "/health",
    }
