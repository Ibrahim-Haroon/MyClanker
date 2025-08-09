from typing import Any
from src.agent.agent import Agent
from src.llm.service.llm_response_service import LlmResponseService
from src.llm.template.llm_template import LlmTemplate


class WebSearchCleanerAgent(Agent):
    def __init__(self, llm_response_service: LlmResponseService):
        self.__llm_response_service = llm_response_service

    def agent_type(self) -> str:
        return "web_search_cleaner_agent"

    def execute(
        self,
        task
    ) -> Any:
        res = self.__llm_response_service.response(
            role="You are a data-cleaning agent that creates structured json objects",
            prompt=LlmTemplate.web_search_parser(task),
        )

        return res
