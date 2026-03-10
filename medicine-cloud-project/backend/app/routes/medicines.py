from fastapi import APIRouter

from app.ai.ai_service import generate_placeholder_response
from app.models.medicine import AskAIRequest, Medicine

router = APIRouter()

# In-memory mock store for initial development.
mock_medicines: list[Medicine] = [
    Medicine(id=1, name="Paracetamol", dosage="500mg", time="08:00"),
    Medicine(id=2, name="Vitamin D", dosage="1000 IU", time="21:00"),
]


@router.get("/medicines", response_model=list[Medicine])
def list_medicines() -> list[Medicine]:
    """Return all mock medicines."""

    return mock_medicines


@router.post("/medicine", response_model=Medicine)
def create_medicine(payload: Medicine) -> Medicine:
    """Create a new medicine in the in-memory store."""

    new_id = len(mock_medicines) + 1
    created = Medicine(id=new_id, name=payload.name, dosage=payload.dosage, time=payload.time)
    mock_medicines.append(created)
    return created


@router.post("/ask-ai")
def ask_ai(payload: AskAIRequest) -> dict[str, str]:
    """Return placeholder AI response for now."""

    response = generate_placeholder_response(payload.question)
    return {"answer": response}
