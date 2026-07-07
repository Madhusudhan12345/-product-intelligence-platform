"""
Simple retrieval + answer evaluation harness.

Measures, per eval question:
  - retrieval recall: fraction of expected source_ids that appear in retrieved evidence
  - retrieval precision: fraction of retrieved evidence whose source_id was expected
  - latency

Run from backend/ with: python -m eval.run_eval
"""
import json
import statistics

from app.agents.orchestrator import orchestrator


def main():
    with open("eval/eval_set.json") as f:
        eval_set = json.load(f)

    recalls, precisions, latencies = [], [], []
    results = []

    for case in eval_set:
        question = case["question"]
        expected = set(case["expected_source_ids"])

        response = orchestrator.run(question)
        retrieved_ids = {c.source_id for c in response.evidence}

        hit = expected & retrieved_ids
        recall = len(hit) / len(expected) if expected else 0
        precision = len(hit) / len(retrieved_ids) if retrieved_ids else 0

        recalls.append(recall)
        precisions.append(precision)
        latencies.append(response.latency_ms)

        results.append({
            "question": question,
            "recall": round(recall, 2),
            "precision": round(precision, 2),
            "latency_ms": response.latency_ms,
            "retrieved_source_ids": sorted(retrieved_ids),
            "expected_source_ids": sorted(expected),
        })

        print(f"Q: {question}")
        print(f"  recall={recall:.2f} precision={precision:.2f} latency={response.latency_ms}ms")
        print(f"  answer preview: {response.answer[:150]}...")
        print()

    print("=" * 60)
    print(f"Avg recall:    {statistics.mean(recalls):.2f}")
    print(f"Avg precision: {statistics.mean(precisions):.2f}")
    print(f"Avg latency:   {statistics.mean(latencies):.0f} ms")

    with open("eval/eval_results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
