# File: src/app.py
import json
import logging
import os
import uuid

from langchain_core.messages import HumanMessage

from graph import build_graph

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initializing graph once during cold start
_GRAPH = build_graph()


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        message = body.get("message")
        thread_id = body.get("thread_id") or str(uuid.uuid4())
        if not message:
            return _response(400, {"error": "message is required"})

        config = {"configurable": {"thread_id": thread_id}}
        # Invoking graph with persistence config
        result = _GRAPH.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=config,
        )
        ai_text = result["messages"][-1].content
        return _response(200, {"thread_id": thread_id, "reply": ai_text})
    except Exception as e:
        # Abort on Error principle - Logging full exception for debugging
        logger.exception("handler failed")
        return _response(500, {"error": type(e).__name__, "detail": str(e)})
