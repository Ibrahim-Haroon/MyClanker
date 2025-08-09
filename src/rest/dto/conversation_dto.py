import uuid
from dataclasses import dataclass


@dataclass
class CreateConversationRequest:
    """Request DTO for creating a new conversation"""
    user_request: str


@dataclass
class CreateConversationResponse:
    """Response DTO for creating a new conversation"""
    conversation_id: uuid.UUID
    response_message: str


@dataclass
class ContinueConversationRequest:
    """Request DTO for continuing an existing conversation"""
    conversation_id: uuid.UUID
    user_request: str


@dataclass
class ContinueConversationResponse:
    """Response DTO for continuing an existing conversation"""
    response_message: str
