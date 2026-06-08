# TV4 A/B Evaluation Report

- Dataset size: 3 questions
- Pipeline root used: `.`
- Best current config: `A_hybrid_with_rerank`

## Overall Scores

| Config | Faithfulness | Answer Relevance | Context Recall | Context Precision | Average |
|---|---:|---:|---:|---:|---:|
| A_hybrid_with_rerank | 0.980 | 0.648 | 0.889 | 1.000 | 0.879 |
| B_hybrid_without_rerank | 0.980 | 0.648 | 0.889 | 1.000 | 0.879 |

## A/B Configurations

- `A_hybrid_with_rerank`: Hybrid retrieval with reranking enabled. top_k=5, threshold=0.3
- `B_hybrid_without_rerank`: Hybrid retrieval with reranking disabled. top_k=5, threshold=0.3

## Worst Performers

| Config | Question | Avg | Recall | Precision | Notes |
|---|---|---:|---:|---:|---|
| A_hybrid_with_rerank | Pipeline có trả về nguồn tài liệu để citation không? | 0.761 | 0.667 | 1.000 | Likely retrieval/context mismatch; inspect top sources. |
| B_hybrid_without_rerank | Pipeline có trả về nguồn tài liệu để citation không? | 0.761 | 0.667 | 1.000 | Likely retrieval/context mismatch; inspect top sources. |
| A_hybrid_with_rerank | Danh mục chất ma túy và tiền chất dùng để làm gì? | 0.902 | 1.000 | 1.000 | Likely retrieval/context mismatch; inspect top sources. |
| B_hybrid_without_rerank | Danh mục chất ma túy và tiền chất dùng để làm gì? | 0.902 | 1.000 | 1.000 | Likely retrieval/context mismatch; inspect top sources. |
| A_hybrid_with_rerank | Luật Phòng, chống ma túy quy định gì về cai nghiện ma túy? | 0.974 | 1.000 | 1.000 | Likely retrieval/context mismatch; inspect top sources. |

## Recommendations

1. Replace smoke dataset with TV3's final `golden_dataset.json` when it lands.
2. Re-run this script after TV1 finalizes `Group/src` so scores reflect the group engine.
3. Investigate cases with low context recall first, because generation cannot be faithful without retrieved evidence.
4. Keep A/B configs small and explicit so demo changes are easy to explain.

## Reproduce

```powershell
python Group/evaluation/run_ab_comparison.py
```
