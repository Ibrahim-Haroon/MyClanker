from typing import Literal
from dataclasses import dataclass


@dataclass
class LlmMessage:
    """
    Represents a message that can be passed in the payload of request to LLM as conversation history
    """
    role: Literal["user", "assistant"]
    content: str
