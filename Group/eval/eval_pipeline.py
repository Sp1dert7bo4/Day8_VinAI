import json
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from deepeval import evaluate
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric,
)
from deepeval.test_case import LLMTestCase
import os
import sys
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_engine import query_rag

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_evaluation(pipeline_func, config_name, dataset_path="eval/golden_dataset.json"):
    print(f"\n--- Đang chạy evaluation cho config: {config_name} ---")
    with open(dataset_path, "r", encoding="utf-8") as f:
        golden_dataset = json.load(f)

    print("Đang tạo câu trả lời cho các câu hỏi trong dataset...")
    test_cases = []
    
    for item in golden_dataset:
        result = pipeline_func(item["question"])
        test_case = LLMTestCase(
            input=item["question"],
            actual_output=result["answer"],
            expected_output=item["expected_answer"],
            retrieval_context=[c["content"] for c in result.get("sources", [])]
        )
        test_cases.append(test_case)

    print("Đang chấm điểm bằng DeepEval...")
    eval_model = "gpt-4o-mini"
    faithfulness = FaithfulnessMetric(threshold=0.5, model=eval_model)
    answer_relevancy = AnswerRelevancyMetric(threshold=0.5, model=eval_model)
    context_recall = ContextualRecallMetric(threshold=0.5, model=eval_model)
    context_precision = ContextualPrecisionMetric(threshold=0.5, model=eval_model)

    test_results_obj = evaluate(
        test_cases=test_cases,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )
    
    records = []
    for test_result in test_results_obj.test_results:
        record = {
            "question": test_result.input,
            "answer": test_result.actual_output,
            "ground_truth": test_result.expected_output,
        }
        for metric_data in test_result.metrics_data:
            metric_name = metric_data.name.lower()
            score = metric_data.score if metric_data.score is not None else 0.0
            if "faithfulness" in metric_name:
                record["faithfulness"] = score
            elif "answer relevancy" in metric_name:
                record["answer_relevancy"] = score
            elif "contextual recall" in metric_name:
                record["context_recall"] = score
            elif "contextual precision" in metric_name:
                record["context_precision"] = score
        records.append(record)
        
    df_results = pd.DataFrame(records)
    mean_scores = df_results[["faithfulness", "answer_relevancy", "context_recall", "context_precision"]].mean()
    worst_performers = df_results.sort_values(by="faithfulness").head(3)

    result_file = "eval/result.md"
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, "a", encoding="utf-8") as f:
        f.write(f"\n## Kết quả Evaluation - Config: {config_name}\n\n")
        f.write("### Bảng điểm chi tiết\n\n")
        f.write(df_results.to_markdown(index=False))
        f.write("\n\n### Điểm trung bình\n\n")
        f.write(mean_scores.to_frame().T.to_markdown(index=False))
        f.write("\n\n### Phân tích Worst Performers (Faithfulness thấp nhất)\n\n")
        f.write(worst_performers[["question", "answer", "faithfulness", "ground_truth"]].to_markdown(index=False))
        f.write("\n\n---\n")

    return df_results

def real_pipeline_A(query):
    return query_rag(query, top_k=5, use_hybrid=True, use_reranker=True)

def real_pipeline_B(query):
    return query_rag(query, top_k=5, use_hybrid=False, use_reranker=False)

if __name__ == "__main__":
    with open("eval/result.md", "w", encoding="utf-8") as f:
        f.write("# Báo cáo kết quả RAG Evaluation\n\n")

    print("Bắt đầu chạy A/B testing với dữ liệu thật...")
    results_A = run_evaluation(real_pipeline_A, "Config A (Hybrid Search + Reranker)")
    results_B = run_evaluation(real_pipeline_B, "Config B (Dense Only, No Reranker)")
    
    mean_A = results_A[["faithfulness", "answer_relevancy", "context_recall", "context_precision"]].mean()
    mean_B = results_B[["faithfulness", "answer_relevancy", "context_recall", "context_precision"]].mean()
    
    comparison_df = pd.DataFrame({
        "Config A": mean_A,
        "Config B": mean_B
    })
    
    print("\n=== BẢNG SO SÁNH TỔNG HỢP ===")
    print(comparison_df)
    
    with open("eval/result.md", "a", encoding="utf-8") as f:
        f.write("\n## Tổng Hợp So Sánh A/B\n\n")
        f.write("Bảng dưới đây so sánh điểm trung bình giữa các cấu hình:\n\n")
        f.write(comparison_df.to_markdown())
        f.write("\n\n---\n")

    print("\nHoàn tất chạy Pipeline. Xem kết quả tại file eval/result.md")
