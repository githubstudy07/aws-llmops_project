# File: crew_app/tasks.py
from crewai import Task
from crew_app.agents import make_researcher, make_copywriter


def make_research_task(researcher) -> Task:
    return Task(
        description=(
            "1. {target_product} を利用しそうなユーザーが、日常で抱えている悩みやストレスを分析してください。\n"
            "2. その悩みに対する解決策を象徴するキーワードを3つ抽出してください。"
        ),
        expected_output="ユーザーの悩み TOP3 と、解決のヒントになるキーワード 3 つのリスト。",
        agent=researcher,
    )


def make_writing_task(copywriter, research_task: Task) -> Task:
    return Task(
        description=(
            "リサーチ結果を活用して、{target_product} の魅力を伝えるキャッチコピーを3案作成してください。\n"
            "各案には、なぜその言葉がターゲットに刺さるのかの短い解説を添えてください。"
        ),
        expected_output="3つのキャッチコピー案（各案に解説付き）。",
        agent=copywriter,
        context=[research_task],
    )
