import uuid
from typing import List, Dict
from threading import RLock
from collections import defaultdict
from src.llm.models.llm_message import LlmMessage
from src.util.singleton import singleton


@singleton
class ConversationMemory:
    """
    Thread-safe class responsible for managing conversation history between the user and LLM.
    """

    def __init__(self):
        self.__lock = RLock()
        self.__store: Dict[uuid.UUID, List[LlmMessage]] = defaultdict(list)

    def history(self, conversation_id: uuid.UUID) -> List[LlmMessage]:
        """
        Returns a copy of the conversation history for the given conversation_id.
        """
        with self.__lock:
            return self.__store[conversation_id].copy()

    def add(self, conversation_id: uuid.UUID, message: LlmMessage) -> None:
        """
        Adds a new message to the conversation history for the given conversation_id.
        """
        with self.__lock:
            self.__store[conversation_id].append(message)
