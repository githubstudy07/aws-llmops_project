# File: local_test.py
"""Local end-to-end test.
Real Bedrock Nova Micro + Real DuckDuckGo search.
Estimated cost: < $0.001 per run.

Usage:
    uv run python local_test.py
"""

import os
import sys

# ---- SQLite hack（Lambda 環境と同じ処理を再現） ----
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

# ---- CrewAI ストレージを /tmp に ----
os.environ.setdefault("CREWAI_STORAGE_DIR", "/tmp/crewai_storage")

from crewai import Crew, Process
from crew_app.agents import make_researcher, make_copywriter
from crew_app.tasks import make_research_task, make_writing_task

# Bedrock Nova Micro（litellm 形式）
LLM_MODEL = "bedrock/us.amazon.nova-micro-v1:0"


def main():
    topic = "AWS Lambda latest features 2026"

    print(f"{'=' * 60}")
    print(f"Local E2E Test")
    print(f"Topic : {topic}")
    print(f"Model : {LLM_MODEL}")
    print(f"{'=' * 60}\n")

    researcher = make_researcher(llm=LLM_MODEL)
    writer = make_copywriter(llm=LLM_MODEL)

    research_task = make_research_task(agent=researcher, topic=topic)
    writing_task = make_writing_task(agent=writer, research_task=research_task, topic=topic)

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    print(f"\n{'=' * 60}")
    print("FINAL OUTPUT:")
    print(f"{'=' * 60}")
    print(result)


if __name__ == "__main__":
    main()
