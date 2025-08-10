from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import requests


class ApiError(Exception):
    def __init__(self, *, status_code: int, endpoint: str, response_text: str) -> None:
        super().__init__(f"Vapi API error {status_code} for {endpoint}: {response_text}")
        self.status_code = status_code
        self.endpoint = endpoint
        self.response_text = response_text


class VapiClient:
    def __init__(self, *, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        # Default headers (acts like an interceptor)
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def _full_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _handle_response(self, *, resp: requests.Response, endpoint: str) -> Any:
        if not resp.ok:
            raise ApiError(status_code=resp.status_code, endpoint=endpoint, response_text=resp.text)
        if not resp.text:
            return None
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text

    def list_workflows(self, *, page: Optional[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        endpoint = "/workflow"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        resp = self.session.get(self._full_url(endpoint), params=params)
        data = self._handle_response(resp=resp, endpoint=endpoint)

        # Normalize to list of workflows
        if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            workflows = data["items"]
        elif isinstance(data, list):
            workflows = data
        else:
            workflows = []

        simplified: List[Dict[str, Any]] = []
        for wf in workflows:
            if not isinstance(wf, dict):
                continue
            simplified.append({"id": wf.get("id"), "name": wf.get("name")})
        return simplified

    def start_workflow_run(
        self,
        *,
        workflow_id: str,
        variables: Dict[str, Any],
        webhook_url: str,
        customer_number: Optional[str] = None,
        phone_number_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Use Create Call with workflow
        # Docs: https://docs.vapi.ai/api-reference/calls/create
        endpoint = "/call"
        # Keep name <= 40 chars
        short_id = workflow_id[:8]
        payload: Dict[str, Any] = {
            "workflowId": workflow_id,
            "name": f"wf:{short_id}",
        }
        # Optional outbound phone call settings
        if phone_number_id:
            payload["phoneNumberId"] = phone_number_id
        if customer_number:
            payload["customer"] = {"number": customer_number}
            payload["type"] = "outboundPhoneCall"
        resp = self.session.post(self._full_url(endpoint), data=json.dumps(payload))
        data = self._handle_response(resp=resp, endpoint=endpoint)
        if isinstance(data, dict):
            return {
                "id": data.get("id"),
                "status": data.get("status"),
                "raw": data,
            }
        return {"raw": data}

