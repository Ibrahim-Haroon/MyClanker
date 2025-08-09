from typing import Any
from src.agent.agent import Agent
from src.llm.service.llm_response_service import LlmResponseService
from src.llm.template.llm_template import LlmTemplate
from src.service.search_service import SearchService


class SearchAgent(Agent):
    def __init__(self, llm_response_service: LlmResponseService):
        self.__llm_response_service = llm_response_service

    def agent_type(self) -> str:
        return "search_agent"

    def execute(
        self,
        task
    ) -> Any:
        query = self.__llm_response_service.response(
            role="You are a search agent that receives a user task and then generates a search query from it",
            prompt=LlmTemplate.web_search_query(task),
        )

        res = SearchService.search(
            query=query,
            city="San Francisco",
            region="San Francisco Bay Area"
        )

        return res
