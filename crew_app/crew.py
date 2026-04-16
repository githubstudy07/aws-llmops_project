# File: crew_app/crew.py
"""Crew 構築 — Phase 9-1 & 9-2."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from crewai import Crew, Process

from crew_app.agents import make_archivist, make_copywriter, make_researcher
from crew_app.tasks import make_archive_task, make_research_task, make_writing_task


def build_crew(topic: str = "latest AI tools 2026", content_id: str | None = None) -> Crew:
    """Crew を構築する。"""
    
    # content_id が未指定の場合は自動生成
    if not content_id:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        content_id = f"research_{ts}"

    researcher = make_researcher()
    copywriter = make_copywriter()
    archivist = make_archivist()

    research_task = make_research_task(agent=researcher, topic=topic)
    writing_task = make_writing_task(agent=copywriter, research_task=research_task, topic=topic)
    
    # 最終成果物 (Writing Task) をアーカイブするタスク
    archive_task = make_archive_task(
        agent=archivist, 
        content_id=content_id, 
        context_task=writing_task
    )

    return Crew(
        agents=[researcher, copywriter, archivist],
        tasks=[research_task, writing_task, archive_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )
