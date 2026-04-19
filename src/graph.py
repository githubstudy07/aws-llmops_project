# File: src/graph.py
from __future__ import annotations

import os
from typing import Annotated, TypedDict

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from checkpointer import build_checkpointer


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def _llm() -> ChatBedrockConverse:
    return ChatBedrockConverse(
        model=os.environ["BEDROCK_MODEL_ID"],  # e.g. "apac.amazon.nova-micro-v1:0"
        region_name=os.environ.get("AWS_REGION_NAME", "ap-northeast-1"),
        temperature=0.2,
    )


def _chat_node(state: State) -> dict:
    resp = _llm().invoke(state["messages"])
    return {"messages": [resp]}


def build_graph():
    g = StateGraph(State)
    g.add_node("chat", _chat_node)
    g.add_edge(START, "chat")
    g.add_edge("chat", END)
    # Compiling with custom checkpointer
    return g.compile(checkpointer=build_checkpointer())
