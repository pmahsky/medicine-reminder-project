from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.medicines import router as medicines_router

# Core FastAPI application instance.
app = FastAPI(title="Medicine Reminder Backend")

# Register route groups.
app.include_router(health_router)
app.include_router(medicines_router)
