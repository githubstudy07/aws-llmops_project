import os
from crewai import Agent, Task, Crew, Process
from langchain_aws import ChatBedrock
from openinference.instrumentation.crewai import CrewAIInstrumentor


def create_marketing_crew():
    """
    マーケティング用 Crew を作成して返す。
    """

    # 0. Lambda の書き込み制限（/tmp のみ）に対応するための設定
    # CrewAI / ChromaDB / Mem0 等のキャッシュディレクトリを /tmp に集約
    os.environ["MEM0_DIR"] = "/tmp/mem0"
    os.environ["CHROMA_DB_DIR"] = "/tmp/chroma_db"
    os.environ["CREWAI_STORAGE_DIR"] = "/tmp/crewai"
    
    for d in ["/tmp/mem0", "/tmp/chroma_db", "/tmp/crewai"]:
        os.makedirs(d, exist_ok=True)

    # 1. 観測性 (Langfuse) のセットアップ
    CrewAIInstrumentor().instrument()

    # 2. LLM (Bedrock Nova Micro) の設定
    # コスト最小化のため、Nova Micro を使用します。
    llm = ChatBedrock(
        model_id="amazon.nova-micro-v1:0",
        model_kwargs={"temperature": 0.3},
        region_name=os.environ.get("AWS_REGION", "ap-northeast-1")
    )

    # 3. エージェントの設計 (Phase 7-1)
    researcher = Agent(
        role="市場トレンド調査員",
        goal="{target_product} に関する消費者の悩みと、解決のキーワードを3つ特定する",
        backstory=(
            "あなたは広告代理店の優秀なリサーチャーです。"
            "消費者が抱える潜在的な不満やニーズを言葉にすることに長けています。"
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=True
    )

    writer = Agent(
        role="クリエイティブ・コピーライター",
        goal="リサーチ結果を元に、消費者の心に刺さるキャッチコピーを3案作成する",
        backstory=(
            "あなたは数々のヒット作を手がけたコピーライターです。"
            "リサーチ結果にある『生の悩み』を、希望を与える言葉に変える天才です。"
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=True
    )

    # 4. タスクの設計 (Phase 7-1)
    research_task = Task(
        description=(
            "1. {target_product} を利用しそうなユーザーが、日常で抱えている悩みやストレスを分析してください。\n"
            "2. その悩みに対する解決策を象徴するキーワードを3つ抽出してください。"
        ),
        expected_output="ユーザーの悩み TOP3 と、解決のヒントになるキーワード 3 つのリスト。",
        agent=researcher
    )

    writing_task = Task(
        description=(
            "リサーチ結果を活用して、{target_product} の魅力を伝えるキャッチコピーを3案作成してください。\n"
            "各案には、なぜその言葉がターゲットに刺さるのかの短い解説を添えてください。"
        ),
        expected_output="3つのキャッチコピー案（各案に解説付き）。",
        agent=writer,
        context=[research_task]
    )

    # 5. Crew の結成
    return Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True
    )
