import logging

from fastapi import APIRouter, HTTPException

from app.ai.ai_service import generate_placeholder_response
from app.models.medicine import AskAIRequest, Medicine, MedicineCreate
from app.services.firestore_service import FirestoreServiceError, add_medicine, get_medicines

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/medicines", response_model=list[Medicine])
def list_medicines() -> list[Medicine]:
    """Fetch medicine documents from Firestore."""
    logger.info(
        "Incoming request for medicines list.",
        extra={"path": "/medicines", "method": "GET", "event": "incoming_request"},
    )
    try:
        return get_medicines()
    except FirestoreServiceError as exc:
        logger.error(
            "Request failed while fetching medicines.",
            extra={"path": "/medicines", "method": "GET", "event": "request_failure"},
        )
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/medicine", response_model=Medicine)
def create_medicine(payload: MedicineCreate) -> Medicine:
    """Create a new medicine document in Firestore."""
    logger.info(
        "Incoming request to create medicine.",
        extra={
            "path": "/medicine",
            "method": "POST",
            "event": "incoming_request",
            "medicine_name": payload.name,
        },
    )
    try:
        return add_medicine(payload)
    except FirestoreServiceError as exc:
        logger.error(
            "Request failed while creating medicine.",
            extra={
                "path": "/medicine",
                "method": "POST",
                "event": "request_failure",
                "medicine_name": payload.name,
            },
        )
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/ask-ai")
def ask_ai(payload: AskAIRequest) -> dict[str, str]:
    """Return placeholder AI response for now."""

    response = generate_placeholder_response(payload.question)
    return {"answer": response}
