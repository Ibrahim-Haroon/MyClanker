from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """
        Returns the type/name of the agent for identification purposes

        :return: agent type identifier
        :rtype: str
        """
        pass

    @abstractmethod
    def execute(
        self,
        task: Any,
    ) -> Any:
        """
        This method is used as a baseline behavior for all Agent Services

        :param task: The task or instruction for the agent to execute
        :return: result from agent execution (type varies by agent implementation)
        :rtype: Any
        """
        pass
