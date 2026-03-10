from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Medicine(BaseModel):
    """Represents a medicine reminder item."""

    id: Optional[str] = Field(default=None, description="Firestore document ID")
    name: str = Field(..., description="Medicine name")
    dosage: str = Field(..., description="Dosage details")
    time: str = Field(..., description="Reminder time, e.g. 08:00")


class MedicineCreate(BaseModel):
    """Payload used to create a new medicine document."""

    name: str = Field(..., description="Medicine name")
    dosage: str = Field(..., description="Dosage details")
    time: str = Field(..., description="Reminder time, e.g. 08:00")


class AskAIRequest(BaseModel):
    """Incoming AI question payload."""

    question: str = Field(..., description="User question for AI")
