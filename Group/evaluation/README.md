# TV4 Evaluation & A/B Analysis

This folder is owned by TV4. It is designed to avoid merge conflicts with the
core RAG engine, UI, and golden dataset work.

## Files

- `ab_configs.py`: A/B retrieval configurations.
- `metrics_utils.py`: dependency-free heuristic metrics.
- `run_ab_comparison.py`: runner that imports `Group/src` when available and
  falls back to completed individual pipelines under `Person/*/src`.
- `results.md`: generated report for demo and final submission.
- `ab_results.json`: detailed generated output, useful for debugging.

## Run

```powershell
python Group/evaluation/run_ab_comparison.py
```

When TV3 adds `Group/evaluation/golden_dataset.json`, this runner will use it
automatically. Until then, it uses a small smoke dataset so the workflow can be
tested early.

