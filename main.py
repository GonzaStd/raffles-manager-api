from fastapi import FastAPI
from routes import buyer, project
app = FastAPI()
app.include_router(buyer.router, tags=["Buyers"])
app.include_router(project.router, tags=["Routers"])
