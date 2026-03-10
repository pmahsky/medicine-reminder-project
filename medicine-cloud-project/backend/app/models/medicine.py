from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Medicine(BaseModel):
    """Represents a medicine reminder item."""

    id: Optional[int] = Field(default=None, description="Auto-assigned medicine ID")
    name: str = Field(..., description="Medicine name")
    dosage: str = Field(..., description="Dosage details")
    time: str = Field(..., description="Reminder time, e.g. 08:00")


class AskAIRequest(BaseModel):
    """Incoming AI question payload."""

    question: str = Field(..., description="User question for AI")
