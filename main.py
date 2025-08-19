from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import buyer, project, raffleset, raffle, entity_auth, manager
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
    title="Raffles Manager API - Entity-Manager System",
    version="2.0.0",
    description="Entity-Manager based raffle management system with composite primary keys",
    lifespan=lifespan
)

# Configure CORS
# For production (Railway), set your frontend domain(s) in BACKEND_CORS_ORIGINS env variable.
# For local development, allow localhost domains.
# Example for Railway: BACKEND_CORS_ORIGINS=["https://your-frontend.railway.app"]
# Example for local: BACKEND_CORS_ORIGINS=["http://localhost:3000"]
origins = []

if settings.BACKEND_CORS_ORIGINS:
    origins.extend(settings.BACKEND_CORS_ORIGINS)
else:
    # Default to localhost for development
    origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

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
    return {"status": "healthy", "system": "entity-manager"}

# Include API routers

# Entity-Manager Authentication Routes
app.include_router(entity_auth.router, prefix="/auth", tags=["Entity & Manager Authentication"])

# Entity Management Routes
app.include_router(buyer.router, tags=["Buyers"])
app.include_router(project.router, tags=["Projects"])
app.include_router(raffleset.router, tags=["Raffle Sets"])
app.include_router(raffle.router, tags=["Raffles"])

# Manager Management Routes
app.include_router(manager.router, tags=["Managers"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Raffles Manager API - Entity-Manager System",
        "version": "2.0.0",
        "architecture": "Entity-Manager with Composite Primary Keys",
        "features": [
            "Entity isolation with predictable numbering",
            "Manager authentication and sale tracking",
            "Composite primary keys for data organization",
            "Automatic database initialization"
        ],
        "auth_endpoints": {
            "entity_register": "/auth/entity/register",
            "entity_login": "/auth/entity/login",
            "manager_register": "/auth/manager/register",
            "manager_login": "/auth/manager/login"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    # Railway sets PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
