# File: crew_app/tasks.py
from crewai import Task
from crew_app.agents import make_researcher, make_copywriter


def make_research_task(researcher) -> Task:
    return Task(
        description=(
            "以下のトピックについて包括的な調査を行ってください。\n"
            "トピック: {topic}\n\n"
            "- 主要な事実と統計を収集する\n"
            "- 信頼できる情報源を特定する\n"
            "- 重要なトレンドや洞察をまとめる"
        ),
        expected_output=(
            "調査レポート（日本語）:\n"
            "- 主要なポイントを箇条書きで 5 点以上\n"
            "- 各ポイントの根拠となる情報を含む"
        ),
        agent=researcher,
    )


def make_writing_task(copywriter, research_task: Task) -> Task:
    return Task(
        description=(
            "リサーチャーの調査結果を元に、以下のトピックに関する記事を執筆してください。\n"
            "トピック: {topic}\n\n"
            "- 読者の興味を引くタイトルと導入文\n"
            "- 調査結果を分かりやすく構造化した本文\n"
            "- 読者へのアクションを促す結論"
        ),
        expected_output=(
            "完成記事（日本語・Markdown 形式）:\n"
            "- タイトル\n"
            "- 導入 (200 字以上)\n"
            "- 本文 (セクション 3 つ以上)\n"
            "- 結論"
        ),
        agent=copywriter,
        context=[research_task],
    )
