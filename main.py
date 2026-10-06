import logging
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .config import settings
from .database import Base, SessionLocal, engine
from .models import User
from .routers import admin, analysis, auth, dashboard, resumes
from .security import hash_password

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("resume-analyzer")


def wait_for_db(retries: int = 30, delay: float = 2.0):
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as exc:
            log.warning("Database not ready (%s/%s): %s", i + 1, retries, str(exc).splitlines()[0])
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database. Check DATABASE_URL.")


def seed_admin():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first():
            db.add(User(full_name="System Admin", email=settings.ADMIN_EMAIL.lower(),
                        hashed_password=hash_password(settings.ADMIN_PASSWORD), role="admin"))
            db.commit()
            log.info("Seeded admin user %s", settings.ADMIN_EMAIL)
    finally:
        db.close()


def warm_up_models():
    try:
        from .ai.matcher import _get_model
        from .ai.preprocessing import get_nlp
        get_nlp()
        _get_model()
        log.info("NLP models loaded")
    except Exception as exc:
        log.warning("Model warm-up failed: %s", exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    seed_admin()
    threading.Thread(target=warm_up_models, daemon=True).start()
    yield


app = FastAPI(title="AI Resume Analyzer & Career Assistant API", version="1.0.0", lifespan=lifespan,
              description="JWT-secured REST API for resume parsing, ATS scoring, job matching and career guidance.")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    msgs = [f"{'.'.join(str(p) for p in e['loc'][1:])}: {e['msg'].removeprefix('Value error, ')}" for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": "; ".join(msgs)})


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    log.exception("Unhandled error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Please try again."})


for r in (auth.router, resumes.router, analysis.router, dashboard.router, admin.router):
    app.include_router(r)


@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok"}
