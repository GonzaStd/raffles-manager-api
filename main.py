from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import buyer, project, raffleset, raffle, auth
from core.config_loader import settings
from typing import cast
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        from database import initialize_database
        initialize_database()
        print("Database initialization completed")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        # Continue anyway - the app can still start and database will be created on first request

    yield  # App runs here

    # Cleanup on shutdown (if needed)
    print("Application shutting down")

app = FastAPI(
    title="Raffles Manager API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "*"  # Allow all origins for now - restrict in production
]

# Add CORS origins from settings if available
if settings.BACKEND_CORS_ORIGINS:
    origins.extend(settings.BACKEND_CORS_ORIGINS)

app.add_middleware(
    cast(type, CORSMiddleware),  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Railway
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/")
async def root():
    return {"message": "Raffles Manager API", "docs": "/docs"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(buyer.router, tags=["Buyers"])
app.include_router(project.router, tags=["Projects"])
app.include_router(raffleset.router, tags=["Raffle Sets"])
app.include_router(raffle.router, tags=["Raffles"])

if __name__ == "__main__":
    import uvicorn
    import os
    # Railway sets PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
