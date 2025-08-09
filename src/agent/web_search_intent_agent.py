from typing import Any
from src.agent.agent import Agent
from src.llm.service.llm_response_service import LlmResponseService
from src.llm.template.llm_template import LlmTemplate


class WebSearchIntentAgent(Agent):
    def __init__(self, llm_response_service: LlmResponseService):
        self.__llm_response_service = llm_response_service

    def agent_type(self) -> str:
        return "web_search_intent_agent"

    def execute(
            self,
            task
    ) -> Any:
        res = self.__llm_response_service.response(
            role="""
                You are a web search intent classification agent. Your job is to read a user’s search query and 
                output the most likely high-level action the user wants to perform
            """,
            prompt=LlmTemplate.web_search_intent(task),
        )

        return res
