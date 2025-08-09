import requests
from textwrap import dedent
from src.agent.web_search_cleaner_agent import WebSearchCleanerAgent
from src.llm.service.openai_llm_response_service import OpenAILlmResponseService
from src.service.search_parser_service import SearchParserService, BusinessDirectory
from src.util.env import Env


class SearchService:
    def __init__(self):
        self.__model = "o4-mini"
        self.__url = "https://api.openai.com/v1/responses"
        self.__api_key = Env()["OPENAI_API_KEY"]
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__api_key}",
        }

    def search(
        self,
        query: str,
        city: str,
        region: str,
        country: str = "us",
        timeout: int = 3 * 60  # 3 minutes default timeout
    ) -> BusinessDirectory:
        payload = {
            "model": self.__model,
            "tools": [{
                "type": "web_search_preview",
                "user_location": {
                    "type": "approximate",
                    "country": country,
                    "city": city,
                    "region": region
                }
            }],
            "input": dedent(f"""
                {query}
                return a JSON object with this exact structure: 
                {{
                    "Business_Name": {{
                        "number": "<phone_number>",
                        "hours": "<opening_hours>",
                        "stars": <rating>,
                        "price_range": "<price_range>"
                    }}
                }}
            """).strip()
        }

        try:
            response = requests.post(
                url=self.__url,
                headers=self.__headers,
                json=payload,
                timeout=timeout
            )
            if response.status_code >= 400:
                raise RuntimeError(f"Search request failed: {response.status_code} {response.reason} - {response.text}")

            return self.parse_web_results(response.json())
        except requests.exceptions.Timeout:
            raise TimeoutError("Brave Search API request timed out")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Search request failed: {str(e)}")

    @staticmethod
    def parse_web_results(response) -> BusinessDirectory:
        res = WebSearchCleanerAgent(OpenAILlmResponseService()).execute(response)

        return SearchParserService().clean(res)
