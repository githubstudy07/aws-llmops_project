import json
import os
import uuid
import time
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")

# Initialize Langfuse Client
client = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY
)

# Initialize LLM
llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    model_kwargs={"temperature": 0.7}
)

# Load Prompts from JSON
def load_prompts(filepath: str) -> Dict:
    """Load variant prompts from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['prompts']

prompts = load_prompts("phase_10_5_7_c_prompts.json")
SYSTEM_PROMPT_A = prompts['variant_a']['system_prompt']
SYSTEM_PROMPT_B = prompts['variant_b']['system_prompt']

def load_dataset(filepath: str) -> Tuple[List[Dict], List[str]]:
    """Load test dataset and domain terms from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['dataset'], data.get('domain_terms', [])

def check_example_presence(response: str) -> Dict:
    """
    C-4: 例示の有無
    日本語・英語の例示表現パターンを検出し、0/7/10の3段階スコアとして返す。
    """
    example_patterns = [
        "例えば", "たとえば", "具体的には", "例として", "例：", "例）",
        "〜など", "などが挙げられ", "ケースとして",
        "for example", "for instance", "e.g.", "such as", "like ",
    ]
    response_lower = response.lower()
    found_patterns = [p for p in example_patterns if p.lower() in response_lower]
    count = len(found_patterns)

    if count == 0:
        example_score = 0.0
    elif count == 1:
        example_score = 7.0
    else:
        example_score = 10.0

    return {
        "has_example": count > 0,
        "example_score": example_score,
        "example_patterns_found": found_patterns,
        "example_pattern_count": count
    }

def measure_structure(response: str) -> Dict:
    """B-3: 段落数とリスト化度を計測"""
    paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
    list_items = re.findall(r'^[\-\*・●▶︎\d+\.]', response, re.MULTILINE)
    has_header = bool(re.search(r'^#{1,3}\s', response, re.MULTILINE))

    return {
        "paragraph_count": len(paragraphs),
        "list_item_count": len(list_items),
        "has_header": has_header,
        "structure_score": min(10.0, len(paragraphs) * 2 + len(list_items) * 0.5)
    }

def measure_term_density(response: str, domain_terms: List[str]) -> Dict:
    """D-1: 専門用語密度"""
    words = response.split()
    if not words:
        return {"term_density": 0.0, "term_count": 0}
    term_count = sum(1 for term in domain_terms if term.lower() in response.lower())
    density = term_count / len(words)
    return {"term_density": round(density, 4), "term_count": term_count}

def evaluate_response(response: str, expected_keywords: List[str], domain_terms: List[str]) -> Dict:
    """Keyword match, length, C-4 example presence, B-3 structure, and D-1 term density eval."""
    response_lower = response.lower()
    keyword_matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)

    # Scoring: keyword match (0-50) + response length indicator (0-50)
    keyword_score = (keyword_matches / len(expected_keywords)) * 50 if expected_keywords else 0
    length_score = min(50, len(response) / 100)  # Normalized to 100 chars = 50 points
    total_score = keyword_score + length_score

    # C-4: 例示の有無
    example_result = check_example_presence(response)
    
    # B-3: 段落数・リスト化度
    structure_result = measure_structure(response)
    
    # D-1: 専門用語密度
    term_density_result = measure_term_density(response, domain_terms)

    return {
        "score": round(total_score, 2),
        "keyword_matches": keyword_matches,
        "response_length": len(response),
        "expected_keywords_count": len(expected_keywords),
        # C-4 追加フィールド
        "has_example": example_result["has_example"],
        "example_score": example_result["example_score"],
        "example_patterns_found": example_result["example_patterns_found"],
        # B-3 追加フィールド
        "paragraph_count": structure_result["paragraph_count"],
        "list_item_count": structure_result["list_item_count"],
        "has_header": structure_result["has_header"],
        "structure_score": structure_result["structure_score"],
        # D-1 追加フィールド
        "term_count": term_density_result["term_count"],
        "term_density": term_density_result["term_density"]
    }

def run_experiment(dataset: List[Dict], domain_terms: List[str], system_prompt: str, variant_name: str, session_id: str) -> List[Dict]:
    """Run all questions with specified system prompt."""
    results = []

    for idx, item in enumerate(dataset):
        question = item['question']
        expected_keywords = item.get('expected_keywords', [])

        try:
            # E-1: レイテンシー計測開始
            invoke_start = time.time()

            # Invoke LLM
            messages = [HumanMessage(content=f"{system_prompt}\n\nQuestion: {question}")]
            response = llm.invoke(messages)
            answer = response.content

            # E-1: レイテンシー計測終了
            latency_sec = round(time.time() - invoke_start, 3)

            # B-2: トークン数取得（langchain_aws の response_metadata から）
            usage = response.response_metadata.get("usage", {})
            input_tokens  = usage.get("inputTokens",  0)
            output_tokens = usage.get("outputTokens", 0)
            total_tokens  = input_tokens + output_tokens

            # Evaluate response
            evaluation = evaluate_response(answer, expected_keywords, domain_terms)

            # Record to Langfuse with trace
            trace_id = f"{session_id}-{variant_name}-{idx}"
            trace = client.trace(
                id=trace_id,
                name=f"Phase10_5_7C_{variant_name}",
                session_id=session_id,
                tags=[variant_name, "ab-test", "prompt-optimization"]
            )

            # Create span for this question
            span = trace.span(
                name=f"question_{item['id']}",
                input={"question": question, "system_prompt": system_prompt[:50] + "..."},
                output={"answer": answer[:100] + "..." if len(answer) > 100 else answer},
                metadata={
                    "variant": variant_name,
                    "latency_sec": latency_sec,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens
                }
            )

            # Record evaluation score (既存)
            client.score(
                trace_id=trace.id,
                name="response_quality",
                value=evaluation['score'],
                comment=f"Keyword matches: {evaluation['keyword_matches']}/{evaluation['expected_keywords_count']}, Response length: {evaluation['response_length']} chars"
            )

            # E-1: レイテンシースコアを記録
            client.score(
                trace_id=trace.id,
                name="latency_sec",
                value=latency_sec,
                comment=f"LLM invoke latency for {variant_name} Q{idx+1}"
            )

            # B-2: トークン数スコアを記録
            client.score(
                trace_id=trace.id,
                name="total_tokens",
                value=float(total_tokens),
                comment=f"input={input_tokens}, output={output_tokens}"
            )

            # C-4: 例示の有無スコアを記録
            client.score(
                trace_id=trace.id,
                name="example_presence",
                value=evaluation["example_score"],
                comment=f"has_example={evaluation['has_example']}, patterns={evaluation['example_patterns_found']}"
            )

            # B-3: 構造スコアを記録
            client.score(
                trace_id=trace.id,
                name="structure_score",
                value=evaluation["structure_score"],
                comment=f"paragraphs={evaluation['paragraph_count']}, list_items={evaluation['list_item_count']}, has_header={evaluation['has_header']}"
            )

            # D-1: 専門用語密度スコアを記録
            client.score(
                trace_id=trace.id,
                name="term_density",
                value=evaluation["term_density"],
                comment=f"term_count={evaluation['term_count']} out of approx {len(answer.split())} words"
            )

            result = {
                "question_id": item['id'],
                "question": question,
                "answer": answer,
                "evaluation": evaluation,
                "trace_id": trace_id,
                # 追加フィールド: 効率性メトリクス
                "latency_sec": latency_sec,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
            results.append(result)
            logger.info(f"[{variant_name}] Q{idx+1}: Score={evaluation['score']} | Latency={latency_sec}s | Tokens={total_tokens}")

        except Exception as e:
            logger.error(f"Error processing question {item['id']}: {str(e)}")
            results.append({
                "question_id": item['id'],
                "question": question,
                "error": str(e)
            })

    return results

def run_ab_test():
    """Execute A/B test with Baseline and Improved prompts."""
    logger.info("=" * 60)
    logger.info("Phase 10-5-7-C: Prompt A/B Test Started")
    logger.info("=" * 60)

    # Load dataset
    dataset, domain_terms = load_dataset("phase_10_5_7_c_dataset.json")
    logger.info(f"Loaded {len(dataset)} questions and {len(domain_terms)} domain terms")

    # Generate session ID
    session_id = f"phase-10-5-7-c-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Run Variant A (Baseline)
    logger.info("\n--- Running Variant A (Baseline) ---")
    results_a = run_experiment(dataset, domain_terms, SYSTEM_PROMPT_A, "Variant_A_Baseline", session_id)

    # Run Variant B (Improved)
    logger.info("\n--- Running Variant B (Improved) ---")
    results_b = run_experiment(dataset, domain_terms, SYSTEM_PROMPT_B, "Variant_B_Improved", session_id)

    # Calculate aggregate metrics
    scores_a = [r['evaluation']['score'] for r in results_a if 'evaluation' in r]
    scores_b = [r['evaluation']['score'] for r in results_b if 'evaluation' in r]

    avg_score_a = sum(scores_a) / len(scores_a) if scores_a else 0
    avg_score_b = sum(scores_b) / len(scores_b) if scores_b else 0
    improvement = ((avg_score_b - avg_score_a) / avg_score_a * 100) if avg_score_a > 0 else 0

    # Prepare comparison report
    report = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "variant_a_baseline": {
                "avg_score": round(avg_score_a, 2),
                "total_questions": len(scores_a),
                "scores": scores_a
            },
            "variant_b_improved": {
                "avg_score": round(avg_score_b, 2),
                "total_questions": len(scores_b),
                "scores": scores_b
            },
            "improvement_percentage": round(improvement, 2)
        },
        "detailed_results": {
            "variant_a": results_a,
            "variant_b": results_b
        }
    }

    # Save report
    report_filename = f"phase_10_5_7_c_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info("\n" + "=" * 60)
    logger.info("A/B Test Comparison Summary")
    logger.info("=" * 60)
    logger.info(f"Variant A (Baseline) Average Score: {avg_score_a:.2f}")
    logger.info(f"Variant B (Improved) Average Score: {avg_score_b:.2f}")
    logger.info(f"Improvement: {improvement:.2f}%")
    logger.info(f"Report saved to: {report_filename}")
    logger.info("=" * 60)

    # Flush Langfuse client to ensure all traces are sent
    client.flush()
    logger.info("Langfuse traces flushed.")

    return report

if __name__ == "__main__":
    run_ab_test()
