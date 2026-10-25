# For: FastAPI application lifecycle initialization and route registration
# Must never: Bind to non-localhost network interfaces or disable CORS restrictions

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from engine.app.core.config import settings
from engine.app.db.connection import get_db
from engine.app.db.schema import init_db
from engine.app.api.auth import router as auth_router
from engine.app.api.vacancies import router as vacancies_router
from engine.app.api.applications import router as applications_router
from engine.app.api.documents import router as documents_router
from engine.app.api.verify import router as verify_router
from engine.app.api.jobs import router as jobs_router
from engine.app.api.review import router as review_router
from engine.app.api.eligibility import router as eligibility_router
from engine.app.api.dashboard import router as dashboard_router
from engine.app.api.reports import router as reports_router
from engine.app.api.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes local SQLite database schema and seeds default accounts."""
    with get_db() as conn:
        init_db(conn)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "app://."],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Formats validation errors into standardized ADVS JSON error envelope."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters.",
                "details": exc.errors()
            }
        }
    )


# Register all API routers
app.include_router(auth_router)
app.include_router(vacancies_router)
app.include_router(applications_router)
app.include_router(documents_router)
app.include_router(verify_router)
app.include_router(jobs_router)
app.include_router(review_router)
app.include_router(eligibility_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(settings_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("engine.app.main:app", host=settings.host, port=settings.port, reload=False)
