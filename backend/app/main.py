import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.rate_limit import add_rate_limit
from app.core.logging import setup_logging
from app.core.security_headers import add_security_headers
from pathlib import Path
from app.database.base import Base
from app.database.session import engine

# Set up logging
setup_logging(log_path=Path("logs/app.log"))

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Non-Profit Donation Platform powered by XRP Ledger",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins during development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add security headers
add_security_headers(app)

# Add rate limiting
add_rate_limit(app)

# Add trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, replace with actual domain
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to the Non-Profit Donation Platform API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 