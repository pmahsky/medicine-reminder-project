from fastapi import APIRouter, HTTPException

from app.ai.ai_service import generate_placeholder_response
from app.models.medicine import AskAIRequest, Medicine, MedicineCreate
from app.services.firestore_service import FirestoreServiceError, add_medicine, get_medicines

router = APIRouter()


@router.get("/medicines", response_model=list[Medicine])
def list_medicines() -> list[Medicine]:
    """Fetch medicine documents from Firestore."""
    try:
        return get_medicines()
    except FirestoreServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/medicine", response_model=Medicine)
def create_medicine(payload: MedicineCreate) -> Medicine:
    """Create a new medicine document in Firestore."""
    try:
        return add_medicine(payload)
    except FirestoreServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/ask-ai")
def ask_ai(payload: AskAIRequest) -> dict[str, str]:
    """Return placeholder AI response for now."""

    response = generate_placeholder_response(payload.question)
    return {"answer": response}
