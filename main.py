from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import buyer, project, raffleset, raffle, auth
from typing import cast

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "*"
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
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(buyer.router, tags=["Buyers"])
app.include_router(project.router, tags=["Projects"])
app.include_router(raffleset.router, tags=["Raffle Sets"])
app.include_router(raffle.router, tags=["Raffles"])
