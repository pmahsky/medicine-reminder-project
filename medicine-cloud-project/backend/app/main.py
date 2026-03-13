from fastapi import FastAPI

from app.logging_config import setup_logging
from app.routes.health import router as health_router
from app.routes.medicines import router as medicines_router

# Configure logging before the application starts serving requests.
setup_logging()

# Core FastAPI application instance.
app = FastAPI(title="Medicine Reminder Backend")


@app.get("/")
def root() -> dict[str, str]:
    """Basic root endpoint for quick service verification."""

    return {"service": "medicine backend running"}


# Register route groups.
app.include_router(health_router)
app.include_router(medicines_router)
