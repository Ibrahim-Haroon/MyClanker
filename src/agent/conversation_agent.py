from typing import Any, List, Optional
from src.agent.agent import Agent
from src.llm.service.llm_response_service import LlmResponseService
from src.llm.models.llm_message import LlmMessage


class ConversationAgent(Agent):
    """Agent that handles general conversation"""

    def __init__(self, llm_response_service: LlmResponseService):
        self.__llm_response_service = llm_response_service

    def agent_type(self) -> str:
        return "conversation_agent"

    def execute(
            self,
            task: str,
            conversation_history: Optional[List[LlmMessage]] = None
    ) -> str:
        """
        Execute the conversation task with optional conversation history

        :param task: The user's request/message
        :param conversation_history: Previous conversation messages for context
        :return: The agent's response
        """
        role = """
        You are Clanker, a helpful AI assistant. You will always be the second agent after the user
        requests a task. You just need to keep bringing the conversation back to the task at hand.
        """

        response = self.__llm_response_service.response(
            role=role,
            prompt=task,
            conversation_history=conversation_history
        )

        return response
