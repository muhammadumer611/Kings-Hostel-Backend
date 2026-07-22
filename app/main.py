from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.core.handlers import register_exception_handlers

from app.routers.auth import router as auth_router
from app.routers.student import router as student_router
from app.routers.room import router as room_router
from app.routers.fee import router as fee_router
from app.routers.complaint import router as complaint_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register Global Exception Handlers
register_exception_handlers(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Deployment ke time isko frontend URL karenge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers
@app.middleware("http")
async def add_security_headers(request, call_next):

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# Routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(room_router)
app.include_router(fee_router)
app.include_router(complaint_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Health"])
def health_check():

    return {
        "success": True,
        "message": "Kings Hostel Backend Running Successfully 🚀",
        "version": settings.VERSION,
    }