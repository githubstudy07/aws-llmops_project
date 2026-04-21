import json
import sys
from typing import Dict, List
from datetime import datetime

def analyze_report(report_filepath: str) -> None:
    """Analyze and display A/B test results with detailed metrics."""

    with open(report_filepath, 'r', encoding='utf-8') as f:
        report = json.load(f)

    summary = report['summary']
    variant_a = summary['variant_a_baseline']
    variant_b = summary['variant_b_improved']
    improvement = summary['improvement_percentage']

    print("\n" + "=" * 70)
    print("PHASE 10-5-7-C: PROMPT A/B TEST ANALYSIS REPORT")
    print("=" * 70)
    print(f"Session ID: {report['session_id']}")
    print(f"Generated: {report['timestamp']}")
    print("=" * 70)

    # Summary Table
    print("\n📊 SUMMARY METRICS")
    print("-" * 70)
    print(f"{'Metric':<40} {'Variant A':<15} {'Variant B':<15}")
    print("-" * 70)
    print(f"{'Average Response Quality Score':<40} {variant_a['avg_score']:<15.2f} {variant_b['avg_score']:<15.2f}")
    print(f"{'Total Questions Tested':<40} {variant_a['total_questions']:<15} {variant_b['total_questions']:<15}")
    print(f"{'Min Score':<40} {min(variant_a['scores']):<15.2f} {min(variant_b['scores']):<15.2f}")
    print(f"{'Max Score':<40} {max(variant_a['scores']):<15.2f} {max(variant_b['scores']):<15.2f}")
    print("-" * 70)

    # Improvement Analysis
    print(f"\n🎯 IMPROVEMENT ANALYSIS")
    print("-" * 70)
    print(f"Improvement: {improvement:+.2f}%")
    if improvement > 0:
        print(f"✅ Variant B (Improved) OUTPERFORMS Variant A")
        print(f"   Absolute gain: {variant_b['avg_score'] - variant_a['avg_score']:.2f} points")
    elif improvement < 0:
        print(f"❌ Variant B (Improved) UNDERPERFORMS Variant A")
        print(f"   Absolute loss: {variant_a['avg_score'] - variant_b['avg_score']:.2f} points")
    else:
        print(f"↔️  Variant B (Improved) is EQUIVALENT to Variant A")
    print("-" * 70)

    # Question-by-question breakdown
    print(f"\n📋 QUESTION-BY-QUESTION BREAKDOWN")
    print("-" * 70)
    detailed = report['detailed_results']

    for idx, (q_a, q_b) in enumerate(zip(detailed['variant_a'], detailed['variant_b'])):
        q_id = q_a.get('question_id', f'q{idx+1}')
        print(f"\nQ{idx+1} ({q_id}): {q_a['question'][:60]}...")

        if 'evaluation' in q_a and 'evaluation' in q_b:
            score_a = q_a['evaluation']['score']
            score_b = q_b['evaluation']['score']
            q_improvement = ((score_b - score_a) / score_a * 100) if score_a > 0 else 0

            print(f"  Variant A: {score_a:.2f} pts | Variant B: {score_b:.2f} pts | Delta: {q_improvement:+.2f}%")
            print(f"  Variant A keywords: {q_a['evaluation']['keyword_matches']}/{q_a['evaluation']['expected_keywords_count']}")
            print(f"  Variant B keywords: {q_b['evaluation']['keyword_matches']}/{q_b['evaluation']['expected_keywords_count']}")
        elif 'error' in q_a or 'error' in q_b:
            print(f"  ⚠️  Error in processing")

    # Learning Insights
    print("\n" + "=" * 70)
    print("💡 LEARNING INSIGHTS (生成AIへの問いの立て方)")
    print("=" * 70)
    print("""
Key Observations:
1. **System Prompt Impact**: Detailed context and role definition in Variant B
   led to more comprehensive answers (length + keyword coverage).

2. **Trade-offs**:
   - More detailed prompts → Higher quality but potentially longer responses
   - Need to balance: information richness vs. conciseness

3. **Success Metrics to Track**:
   - Keyword coverage (did AI answer address key concepts?)
   - Response length (is it proportional to question complexity?)
   - User satisfaction (would need manual evaluation in production)

4. **Next Steps for Phase 10-5-7-D (Automated Evaluation)**:
   - Define explicit evaluation rubric (精度/関連性/説得力)
   - Build LLM-as-a-Judge for quality scoring
   - Accumulate test dataset (成功例 + 失敗例)
""")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_ab_test_results.py <report_filepath>")
        sys.exit(1)

    report_filepath = sys.argv[1]
    analyze_report(report_filepath)
