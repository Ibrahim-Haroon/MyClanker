from abc import ABC, abstractmethod
from typing import Optional, List
from src.llm.models.llm_message import LlmMessage


class LlmResponseService(ABC):
    @abstractmethod
    def response(
            self,
            role: str,
            prompt: str,
            conversation_history: Optional[List[LlmMessage]],
            timeout: Optional[int] = None
    ) -> str:
        """
        This method is used as a baseline behavior for all LLM Response Services

        :param role: The behavior/persona for the model to inherit
        :param prompt: The task for the model to complete
        :param conversation_history: The conversation history to provide context for the model
        :param timeout: Amount of seconds to wait before throwing requests.exceptions.Timeout
        :return: response from LLM
        :rtype: str
        :exception: requests.exceptions.Timeout
        """
        pass
