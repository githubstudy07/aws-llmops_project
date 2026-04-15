# File: crew_app/crew.py
import os
from crewai import Crew, Process
from crew_app.agents import make_researcher, make_copywriter
from crew_app.tasks import make_research_task, make_writing_task


def build_crew() -> Crew:
    """
    Crew を構築して返す。
    """
    researcher = make_researcher()
    copywriter = make_copywriter()

    research_task = make_research_task(researcher)
    writing_task = make_writing_task(copywriter, research_task)

    crew = Crew(
        agents=[researcher, copywriter],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=False,
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
    return crew
