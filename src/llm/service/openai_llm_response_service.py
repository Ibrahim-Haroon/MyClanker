import requests
from typing import override, Optional, List
from src.util.env import Env
from src.llm.models.llm_message import LlmMessage
from src.llm.service.llm_response_service import LlmResponseService


class OpenAILlmResponseService(LlmResponseService):
    def __init__(self, model: str = "gpt-5-chat-latest"):
        self.__model = model
        self.__url = "https://api.openai.com/v1/chat/completions"
        self.__api_key = Env()["OPENAI_API_KEY"]
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__api_key}",
        }

    @property
    def model(self) -> str:
        return self.__model

    @override
    def response(
            self,
            role: str,
            prompt: str,
            conversation_history: Optional[List[LlmMessage]] = None,
            timeout: Optional[int] = None
    ) -> str:
        payload = {
            "model": self.__model,
            "messages": [
                {
                    "role": "system",
                    "content": role
                },
                *[
                    {
                        "role": m.role,
                        "content": m.content
                    } for m in (conversation_history or [])
                ],
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = requests.post(
                url=self.__url,
                headers=self.__headers,
                json=payload,
                timeout=timeout
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("OpenAI must be down or increase timeout duration")

        response_data = response.json()
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError("No content found in the response")
