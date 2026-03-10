from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore

from app.models.medicine import Medicine, MedicineCreate

COLLECTION_NAME = "medicines"


class FirestoreServiceError(Exception):
    """Raised when a Firestore read or write operation fails."""


def _get_client() -> firestore.Client:
    """Create a Firestore client using Application Default Credentials."""

    return firestore.Client()


def get_medicines() -> list[Medicine]:
    """Fetch all medicine documents from Firestore."""
    try:
        client = _get_client()
        docs = client.collection(COLLECTION_NAME).stream()
        medicines: list[Medicine] = []

        for doc in docs:
            data = doc.to_dict() or {}
            medicines.append(
                Medicine(
                    id=doc.id,
                    name=data.get("name", ""),
                    dosage=data.get("dosage", ""),
                    time=data.get("time", ""),
                )
            )

        return medicines
    except GoogleAPICallError as exc:
        raise FirestoreServiceError("Failed to fetch medicines from Firestore.") from exc


def add_medicine(payload: MedicineCreate) -> Medicine:
    """Insert a medicine document into Firestore and return the stored record."""
    try:
        client = _get_client()
        doc_ref = client.collection(COLLECTION_NAME).document()
        doc_ref.set(
            {
                "name": payload.name,
                "dosage": payload.dosage,
                "time": payload.time,
            }
        )

        return Medicine(
            id=doc_ref.id,
            name=payload.name,
            dosage=payload.dosage,
            time=payload.time,
        )
    except GoogleAPICallError as exc:
        raise FirestoreServiceError("Failed to add medicine to Firestore.") from exc
