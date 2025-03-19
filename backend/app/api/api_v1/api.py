from fastapi import APIRouter
from app.api import auth
from app.api.api_v1.endpoints import users, npos, donations, admin, health

api_router = APIRouter()

# Include auth router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include other routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(npos.router, prefix="/npos", tags=["npos"])
api_router.include_router(donations.router, prefix="/donations", tags=["donations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(health.router, tags=["health"]) 