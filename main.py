from fastapi import FastAPI
from routes import buyer
app = FastAPI()
app.include_router(buyer.router, tags=["Buyers"])
