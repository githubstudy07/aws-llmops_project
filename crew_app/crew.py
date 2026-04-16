# File: crew_app/crew.py
"""Crew 構築"""

from __future__ import annotations

import os
from crewai import Crew, Process

from crew_app.agents import make_researcher, make_copywriter
from crew_app.tasks import make_research_task, make_writing_task


def build_crew(topic: str = "latest AI tools 2026") -> Crew:
    """Crew を構築する。

    Args:
        topic: 調査テーマ

    Returns:
        実行可能な Crew オブジェクト
    """
    researcher = make_researcher()
    copywriter = make_copywriter()

    research_task = make_research_task(agent=researcher, topic=topic)
    writing_task = make_writing_task(agent=copywriter, research_task=research_task, topic=topic)

    return Crew(
        agents=[researcher, copywriter],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
        memory=True,
        embedder={
            "provider": "aws_bedrock",
            "config": {
                "model": "amazon.titan-embed-text-v2:0",
                "vector_dimension": 1024,
            },
        },
        storage_path=os.environ.get("CREWAI_STORAGE_DIR", "/tmp/crewai_storage"),
    )
