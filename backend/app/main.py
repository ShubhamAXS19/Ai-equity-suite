from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.routers import companies, settings, research, analyzer, news
from app.services.news_scheduler import start_scheduler, stop_scheduler

app = FastAPI(title="AI Equity Research Suite API")

import os

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


app.include_router(companies.router)
app.include_router(settings.router)
app.include_router(research.router)
app.include_router(analyzer.router)
app.include_router(news.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
