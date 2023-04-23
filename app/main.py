from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import get_logger, APP_NAME, APP_VERSION
from app.routes import market

# Initialize logger
logger = get_logger()

# Define tags metadata for documentation
tags_metadata = [
    {
        "name": "market",
        "description": "Market Options API.",
    }
]

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="LNG Market API",
    redoc_url="/",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    reload=True,
    cache=False
)

# Define allowed origins for CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
]

# Add CORS middleware to app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency function to get a database session


def get_db():
    """
    Provides a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Include router for market endpoints
app.include_router(market.router)


# Define health endpoint for testing
@app.get("/health")
async def health():
    """
    Health check endpoint for testing.
    """
    return "OK"
