from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint for uptime checks."""

    return {"status": "ok"}
