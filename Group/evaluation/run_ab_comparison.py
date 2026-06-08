"""Run A/B comparison for the group RAG pipeline.

Usage:
    python Group/evaluation/run_ab_comparison.py

The runner first tries to import the group pipeline from Group/src. If the group
engine is not ready yet, it falls back to any completed individual pipeline under
Person/*/src so TV4 can keep producing reports without blocking other members.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from statistics import mean

from ab_configs import AB_CONFIGS
from metrics_utils import score_case, summarize, token_overlap


EVALUATION_DIR = Path(__file__).resolve().parent
GROUP_DIR = EVALUATION_DIR.parent
REPO_ROOT = GROUP_DIR.parent
RESULTS_PATH = EVALUATION_DIR / "results.md"
DETAILS_PATH = EVALUATION_DIR / "ab_results.json"


SMOKE_DATASET = [
    {
        "question": "Luật Phòng, chống ma túy quy định gì về cai nghiện ma túy?",
        "expected_answer": "Luật quy định các hình thức cai nghiện và trách nhiệm quản lý người sử dụng trái phép chất ma túy.",
        "expected_context": "cai nghiện ma túy",
    },
    {
        "question": "Danh mục chất ma túy và tiền chất dùng để làm gì?",
        "expected_answer": "Danh mục dùng để quản lý các chất ma túy, tiền chất và làm căn cứ kiểm soát theo pháp luật.",
        "expected_context": "danh mục chất ma túy tiền chất",
    },
    {
        "question": "Pipeline có trả về nguồn tài liệu để citation không?",
        "expected_answer": "Pipeline cần trả về nội dung, điểm số và metadata nguồn để tạo citation.",
        "expected_context": "source citation metadata",
    },
]


def load_dataset() -> list[dict]:
    candidates = [
        EVALUATION_DIR / "golden_dataset.json",
        REPO_ROOT / "group_project" / "evaluation" / "golden_dataset.json",
    ]
    for path in candidates:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return SMOKE_DATASET


def _candidate_pipeline_roots() -> list[Path]:
    roots = []
    if (GROUP_DIR / "src" / "task9_retrieval_pipeline.py").exists():
        roots.append(GROUP_DIR)
    for person_dir in sorted((REPO_ROOT / "Person").glob("*")):
        if (person_dir / "src" / "task9_retrieval_pipeline.py").exists():
            roots.append(person_dir)
    return roots


def _fallback_markdown_docs() -> list[dict]:
    docs = []
    search_roots = [GROUP_DIR / "data" / "standardized", REPO_ROOT / "Person"]
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for md_file in search_root.rglob("*.md"):
            if "report" in md_file.parts:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if len(content.strip()) < 100:
                continue
            docs.append(
                {
                    "content": content[:1500],
                    "metadata": {
                        "source": md_file.name,
                        "path": str(md_file.relative_to(REPO_ROOT)),
                        "type": "legal" if "legal" in md_file.parts else "news",
                    },
                }
            )
    return docs


def _fallback_retrieve(query: str, top_k: int = 5, score_threshold: float = 0.0, use_reranking: bool = True):
    docs = _fallback_markdown_docs()
    ranked = []
    for doc in docs:
        score = token_overlap(query, doc["content"])
        if score > 0:
            ranked.append({**doc, "score": float(score), "source": "fallback_markdown"})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def _fallback_generate(query: str, top_k: int = 5):
    retrieved = _fallback_retrieve(query, top_k=top_k)
    answer = _answer_from_retrieval(query, retrieved)
    return {"answer": answer, "sources": retrieved, "retrieval_source": "fallback_markdown"}


def load_pipeline():
    errors = []
    for root in _candidate_pipeline_roots():
        sys.path.insert(0, str(root))
        try:
            retrieval_module = importlib.import_module("src.task9_retrieval_pipeline")
            generation_module = importlib.import_module("src.task10_generation")
            return {
                "root": root,
                "retrieve": retrieval_module.retrieve,
                "generate_with_citation": generation_module.generate_with_citation,
            }
        except Exception as exc:  # Keep trying other members' pipelines.
            errors.append(f"{root}: {exc}")
            sys.path.pop(0)
            for module_name in list(sys.modules):
                if module_name == "src" or module_name.startswith("src."):
                    sys.modules.pop(module_name, None)

    return {
        "root": REPO_ROOT,
        "retrieve": _fallback_retrieve,
        "generate_with_citation": _fallback_generate,
        "warnings": errors,
    }


def _answer_from_retrieval(question: str, retrieved: list[dict]) -> str:
    if not retrieved:
        return "I cannot verify this information from the available context."
    snippets = []
    for item in retrieved[:3]:
        source = item.get("metadata", {}).get("source", "unknown source")
        content = item.get("content", "").replace("\n", " ").strip()
        snippets.append(f"{content[:240]} [{source}]")
    return " ".join(snippets)


def run_config(config_name: str, config: dict, dataset: list[dict], pipeline: dict) -> list[dict]:
    rows = []
    retrieve = pipeline["retrieve"]

    for item in dataset:
        question = item["question"]
        try:
            retrieved = retrieve(
                question,
                top_k=config["top_k"],
                score_threshold=config["score_threshold"],
                use_reranking=config["use_reranking"],
            )
            error = ""
        except TypeError:
            retrieved = retrieve(question, top_k=config["top_k"])
            error = "Pipeline does not support all config parameters."
        except Exception as exc:
            retrieved = []
            error = str(exc)

        answer = _answer_from_retrieval(question, retrieved)
        rows.append(
            {
                "config": config_name,
                "question": question,
                "retrieved_count": len(retrieved),
                "top_source": retrieved[0].get("metadata", {}).get("source", "") if retrieved else "",
                "answer": answer,
                "scores": score_case(item, retrieved, answer),
                "error": error,
            }
        )
    return rows


def worst_performers(all_rows: dict[str, list[dict]], limit: int = 5) -> list[dict]:
    combined = []
    for config_name, rows in all_rows.items():
        for row in rows:
            combined.append(
                {
                    "config": config_name,
                    "question": row["question"],
                    "average": row["scores"]["average"],
                    "context_recall": row["scores"]["context_recall"],
                    "context_precision": row["scores"]["context_precision"],
                    "error": row["error"],
                }
            )
    return sorted(combined, key=lambda row: row["average"])[:limit]


def write_report(dataset: list[dict], pipeline_root: Path, all_rows: dict[str, list[dict]]):
    summaries = {name: summarize(rows) for name, rows in all_rows.items()}
    best_config = max(summaries, key=lambda name: summaries[name]["average"]) if summaries else "N/A"

    lines = [
        "# TV4 A/B Evaluation Report",
        "",
        f"- Dataset size: {len(dataset)} questions",
        f"- Pipeline root used: `{pipeline_root.relative_to(REPO_ROOT)}`",
        f"- Best current config: `{best_config}`",
        "",
        "## Overall Scores",
        "",
        "| Config | Faithfulness | Answer Relevance | Context Recall | Context Precision | Average |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, scores in summaries.items():
        lines.append(
            f"| {name} | {scores['faithfulness']:.3f} | {scores['answer_relevance']:.3f} | "
            f"{scores['context_recall']:.3f} | {scores['context_precision']:.3f} | {scores['average']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## A/B Configurations",
            "",
        ]
    )
    for name, config in AB_CONFIGS.items():
        lines.append(f"- `{name}`: {config['description']} top_k={config['top_k']}, threshold={config['score_threshold']}")

    lines.extend(
        [
            "",
            "## Worst Performers",
            "",
            "| Config | Question | Avg | Recall | Precision | Notes |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in worst_performers(all_rows):
        note = row["error"] or "Likely retrieval/context mismatch; inspect top sources."
        lines.append(
            f"| {row['config']} | {row['question']} | {row['average']:.3f} | "
            f"{row['context_recall']:.3f} | {row['context_precision']:.3f} | {note} |"
        )

    lines.extend(
        [
            "",
            "## Recommendations",
            "",
            "1. Replace smoke dataset with TV3's final `golden_dataset.json` when it lands.",
            "2. Re-run this script after TV1 finalizes `Group/src` so scores reflect the group engine.",
            "3. Investigate cases with low context recall first, because generation cannot be faithful without retrieved evidence.",
            "4. Keep A/B configs small and explicit so demo changes are easy to explain.",
            "",
            "## Reproduce",
            "",
            "```powershell",
            "python Group/evaluation/run_ab_comparison.py",
            "```",
            "",
        ]
    )
    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    dataset = load_dataset()
    pipeline = load_pipeline()
    all_rows = {
        name: run_config(name, config, dataset, pipeline)
        for name, config in AB_CONFIGS.items()
    }
    DETAILS_PATH.write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_report(dataset, pipeline["root"], all_rows)
    print(f"Pipeline root: {pipeline['root']}")
    print(f"Results written to: {RESULTS_PATH}")
    for name, rows in all_rows.items():
        print(name, summarize(rows))


if __name__ == "__main__":
    main()
