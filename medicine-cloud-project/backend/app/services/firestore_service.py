import logging

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore

from app.models.medicine import Medicine, MedicineCreate

COLLECTION_NAME = "medicines"
logger = logging.getLogger(__name__)


class FirestoreServiceError(Exception):
    """Raised when a Firestore read or write operation fails."""


def _get_client() -> firestore.Client:
    """Create a Firestore client using Application Default Credentials."""
    logger.info(
        "Initializing Firestore client.",
        extra={"event": "firestore_client_init", "collection": COLLECTION_NAME},
    )
    return firestore.Client()


def get_medicines() -> list[Medicine]:
    """Fetch all medicine documents from Firestore."""
    try:
        client = _get_client()
        logger.info(
            "Fetching medicines from Firestore.",
            extra={"event": "firestore_read", "collection": COLLECTION_NAME},
        )
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

        logger.info(
            "Fetched medicines from Firestore.",
            extra={
                "event": "firestore_read_complete",
                "collection": COLLECTION_NAME,
                "document_count": len(medicines),
            },
        )
        return medicines
    except GoogleAPICallError as exc:
        logger.exception(
            "Firestore read failed.",
            extra={"event": "firestore_read_error", "collection": COLLECTION_NAME},
        )
        raise FirestoreServiceError("Failed to fetch medicines from Firestore.") from exc


def add_medicine(payload: MedicineCreate) -> Medicine:
    """Insert a medicine document into Firestore and return the stored record."""
    try:
        client = _get_client()
        logger.info(
            "Writing medicine to Firestore.",
            extra={
                "event": "firestore_write",
                "collection": COLLECTION_NAME,
                "medicine_name": payload.name,
            },
        )
        doc_ref = client.collection(COLLECTION_NAME).document()
        doc_ref.set(
            {
                "name": payload.name,
                "dosage": payload.dosage,
                "time": payload.time,
            }
        )

        logger.info(
            "Medicine written to Firestore.",
            extra={
                "event": "firestore_write_complete",
                "collection": COLLECTION_NAME,
                "document_id": doc_ref.id,
                "medicine_name": payload.name,
            },
        )
        return Medicine(
            id=doc_ref.id,
            name=payload.name,
            dosage=payload.dosage,
            time=payload.time,
        )
    except GoogleAPICallError as exc:
        logger.exception(
            "Firestore write failed.",
            extra={
                "event": "firestore_write_error",
                "collection": COLLECTION_NAME,
                "medicine_name": payload.name,
            },
        )
        raise FirestoreServiceError("Failed to add medicine to Firestore.") from exc
