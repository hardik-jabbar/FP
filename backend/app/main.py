from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router  # type: ignore
from app.routers.diagnostics import router as diagnostics_router  # type: ignore

app = FastAPI(title="FarmPower API")

# Basic CORS – adjust as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(diagnostics_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
