# File: src/checkpointer.py
"""
DynamoDB-backed CheckpointSaver for LangGraph 0.6.x.

Table schema (変更不可):
  PK: thread_id      (S)
  SK: checkpoint_id  (S)
Attributes:
  checkpoint     (B, msgpack-serialized)
  metadata       (B, msgpack-serialized)
  parent_id      (S, nullable)
  ts             (S, ISO-8601)
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterator, Optional, Sequence

import boto3
from boto3.dynamodb.conditions import Key
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer


class DynamoDBSaver(BaseCheckpointSaver):
    """Minimal sync DynamoDB checkpoint saver (Lambda + REST API 向け)."""

    def __init__(
        self,
        table_name: str,
        region_name: str | None = None,
        serde: SerializerProtocol | None = None,
    ) -> None:
        super().__init__(serde=serde or JsonPlusSerializer())
        self._table_name = table_name
        self._ddb = boto3.resource("dynamodb", region_name=region_name)
        self._table = self._ddb.Table(table_name)

    # ---------- helpers ----------
    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ---------- BaseCheckpointSaver API ----------
    def put(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, str | int | float],
    ) -> dict[str, Any]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]
        parent_id = config["configurable"].get("checkpoint_id")

        # Serializing Checkpoint and Metadata
        ckpt_type, ckpt_bytes = self.serde.dumps_typed(checkpoint)
        meta_type, meta_bytes = self.serde.dumps_typed(metadata)

        self._table.put_item(
            Item={
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "parent_id": parent_id or "",
                "ts": self._now_iso(),
                "ckpt_type": ckpt_type,
                "ckpt": ckpt_bytes,
                "meta_type": meta_type,
                "meta": meta_bytes,
            }
        )
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

    def put_writes(
        self,
        config: dict[str, Any],
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        # 最小実装：intermediate writes を単一項目に畳み込み
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        w_type, w_bytes = self.serde.dumps_typed(list(writes))
        self._table.update_item(
            Key={"thread_id": thread_id, "checkpoint_id": checkpoint_id},
            UpdateExpression="SET #wt = :t, #wb = :b, #tid = :tid",
            ExpressionAttributeNames={
                "#wt": "writes_type",
                "#wb": "writes_b",
                "#tid": "task_id",
            },
            ExpressionAttributeValues={
                ":t": w_type,
                ":b": w_bytes,
                ":tid": task_id,
            },
        )

    def get_tuple(self, config: dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id")

        if checkpoint_id:
            resp = self._table.get_item(
                Key={"thread_id": thread_id, "checkpoint_id": checkpoint_id}
            )
            item = resp.get("Item")
        else:
            resp = self._table.query(
                KeyConditionExpression=Key("thread_id").eq(thread_id),
                ScanIndexForward=False,
                Limit=1,
            )
            items = resp.get("Items", [])
            item = items[0] if items else None

        if not item:
            return None

        # Deserializing Checkpoint and Metadata (using .value for Binary items from DynamoDB)
        checkpoint = self.serde.loads_typed((item["ckpt_type"], item["ckpt"].value))
        metadata = self.serde.loads_typed((item["meta_type"], item["meta"].value))
        parent_id = item.get("parent_id") or None

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": item["checkpoint_id"],
                }
            },
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=(
                {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": parent_id,
                    }
                }
                if parent_id
                else None
            ),
        )

    def list(
        self,
        config: Optional[dict[str, Any]],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        if not config:
            return iter(())
        thread_id = config["configurable"]["thread_id"]
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": Key("thread_id").eq(thread_id),
            "ScanIndexForward": False,
        }
        if limit:
            kwargs["Limit"] = limit
        resp = self._table.query(**kwargs)
        for item in resp.get("Items", []):
            checkpoint = self.serde.loads_typed((item["ckpt_type"], item["ckpt"].value))
            metadata = self.serde.loads_typed((item["meta_type"], item["meta"].value))
            yield CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": item["checkpoint_id"],
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=None,
            )


def build_checkpointer() -> DynamoDBSaver:
    table = os.environ["CHECKPOINT_TABLE"]
    region = os.environ.get("AWS_REGION_NAME") or os.environ.get("AWS_REGION")
    return DynamoDBSaver(table_name=table, region_name=region)
