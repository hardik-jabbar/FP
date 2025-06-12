from fastapi import FastAPI
from .routers import marketplace
from .core.database import engine
from .models import product

product.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FarmPower Marketplace API")

app.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FarmPower Marketplace API"} 