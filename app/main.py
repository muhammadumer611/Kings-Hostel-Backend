from fastapi import FastAPI
from app.firebase.firebase import db
from app.config.settings import settings
from app.routers.auth import router as auth_router
from app.routers.student import router as student_router
from app.routers.room import router as room_router
from app.routers.fee import router as fee_router
from app.routers.complaint import router as complaint_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(room_router)
app.include_router(fee_router)
app.include_router(complaint_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "message": "Kings Hostel Backend Running Successfully 🚀"
    }