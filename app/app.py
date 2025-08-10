from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from .memory import store
from .schemas import TriggerRequest, WebhookEvent
from .vapi_client import ApiError, VapiClient


def register_vapi_routes(app: Flask) -> None:
    """Register Vapi-related routes and error handlers on an existing Flask app."""
    load_dotenv()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    vapi_api_key = os.getenv("VAPI_API_KEY", "").strip()
    vapi_base_url = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai").strip()
    public_url = os.getenv("PUBLIC_URL", "http://localhost:5000").strip()
    default_phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID", "").strip() or None

    if not vapi_api_key:
        logger.warning("VAPI_API_KEY is not set. Set it in .env.")

    client = VapiClient(base_url=vapi_base_url, api_key=vapi_api_key)

    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return (
            jsonify(
                {
                    "error": {
                        "status_code": err.status_code,
                        "endpoint": err.endpoint,
                        "message": err.response_text,
                    }
                }
            ),
            err.status_code,
        )

    @app.errorhandler(Exception)
    def handle_exception(err: Exception):
        logger.exception("Unhandled error")
        return jsonify({"error": {"message": str(err)}}), 500

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.get("/workflows")
    def workflows():
        page_param = request.args.get("page")
        limit_param = request.args.get("limit")
        page = int(page_param) if page_param is not None else None
        limit = int(limit_param) if limit_param is not None else None

        items = client.list_workflows(page=page, limit=limit)
        return jsonify(items)

    @app.post("/trigger")
    def trigger():
        data = request.get_json(force=True, silent=False)
        payload = TriggerRequest.model_validate(data)

        variables = {
            "user": payload.user,
            "service_type": payload.serviceType,
            "time_window": payload.window,
        }
        webhook_url = f"{public_url.rstrip('/')}/webhooks/vapi"

        phone_number_id = payload.phoneNumberId or default_phone_number_id

        result = client.start_workflow_run(
            workflow_id=payload.workflowId,
            variables=variables,
            webhook_url=webhook_url,
            customer_number=payload.customerNumber,
            phone_number_id=phone_number_id,
        )

        return (
            jsonify(
                {
                    "id": result.get("id"),
                    "status": result.get("status"),
                    "variables": variables,
                }
            ),
            201,
        )

    def _extract_booking_summary(event: Dict[str, Any]) -> Dict[str, Any]:
        # Best-effort extraction of relevant fields if present
        fields: Dict[str, Any] = {}
        for key in ["id", "status", "runId", "callId"]:
            if key in event:
                fields[key] = event.get(key)

        # Try nested structures
        chosen_date = (
            event.get("chosen_date")
            or event.get("date")
            or event.get("booking", {}).get("date")
        )
        chosen_time = (
            event.get("chosen_time")
            or event.get("time")
            or event.get("booking", {}).get("time")
        )
        price = event.get("price") or event.get("booking", {}).get("price")
        duration = event.get("duration") or event.get("booking", {}).get("duration")

        business = event.get("business") or {}
        business_name = business.get("name") or event.get("business_name")
        business_address = business.get("address") or event.get("business_address")
        business_phone = business.get("phone") or event.get("business_phone")

        if chosen_date is not None:
            fields["chosen_date"] = chosen_date
        if chosen_time is not None:
            fields["chosen_time"] = chosen_time
        if price is not None:
            fields["price"] = price
        if duration is not None:
            fields["duration"] = duration
        if business_name is not None:
            fields["business_name"] = business_name
        if business_address is not None:
            fields["business_address"] = business_address
        if business_phone is not None:
            fields["business_phone"] = business_phone
        return fields

    def _verify_signature_stub(req) -> bool:
        # TODO: Implement signature verification if Vapi provides one
        return True

    @app.post("/webhooks/vapi")
    def webhook_receiver():
        if not _verify_signature_stub(request):
            return jsonify({"ok": False, "error": "invalid signature"}), 401

        event_json = request.get_json(force=True, silent=True) or {}
        # Validate but accept extra
        _ = WebhookEvent.model_validate(event_json)

        # Store last payload
        store.set_last(event_json)

        # Log key fields
        summary = _extract_booking_summary(event_json)
        logging.getLogger(__name__).info("Webhook summary: %s", json.dumps(summary))

        return jsonify({"ok": True})

    @app.get("/debug/last-webhook")
    def last_webhook():
        return jsonify(store.get_last() or {})

    # Print curl examples on startup
    logger.info("""Curl examples:
# 1) List workflows
curl -s http://localhost:5000/workflows | jq

# 2) Trigger a workflow (replace WF_ID)
curl -s -X POST http://localhost:5000/trigger \
  -H "Content-Type: application/json" \
  -d "{\"workflowId\":\"WF_ID\",\"user\":\"Marco\",\"serviceType\":\"men's haircut\",\"window\":\"Mon–Fri afternoon\"}" | jq

# 3) Inspect the last webhook payload
curl -s http://localhost:5000/debug/last-webhook | jq""")


def create_app() -> Flask:
    app = Flask(__name__)
    # Do not enable CORS here to avoid double middleware; let main app decide
    register_vapi_routes(app)
    return app


if __name__ == "__main__":
    # Standalone run for this module
    app = create_app()
    port_str = os.getenv("PORT", "5000")
    try:
        port = int(port_str)
    except ValueError:
        port = 5000
    app.run(host="0.0.0.0", port=port, debug=True)

