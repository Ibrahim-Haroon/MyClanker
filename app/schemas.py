from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class TriggerRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    workflowId: str = Field(min_length=1)
    user: str = Field(min_length=1)
    serviceType: str = Field(min_length=1)
    window: str = Field(min_length=1)
    customerNumber: Optional[str] = None
    phoneNumberId: Optional[str] = None


class WebhookEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    status: Optional[str] = None
    # Accept any additional fields
    data: Optional[Dict[str, Any]] = None

