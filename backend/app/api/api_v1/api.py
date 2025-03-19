from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, donations, npos, users, admin, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(donations.router, prefix="/donations", tags=["donations"])
api_router.include_router(npos.router, prefix="/npos", tags=["non-profit organizations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(health.router, tags=["health"]) 