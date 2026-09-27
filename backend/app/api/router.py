from fastapi import APIRouter
from app.api.routes import health, analyze

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
