from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import articles, bills, guidance, notifications, rights
from .eye.scheduler import start_scheduler, stop_scheduler
from .seed import seed

app = FastAPI(
    title="CitizenEye API",
    description="Autonomous civic intelligence platform backend — the CivicPulse core.",
    version="1.0.0",
)

origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(rights.router)
app.include_router(bills.router)
app.include_router(notifications.router)
app.include_router(guidance.router)


@app.on_event("startup")
def on_startup():
    seed()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.get("/")
def root():
    return {"name": "CitizenEye API", "status": "ok", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}
