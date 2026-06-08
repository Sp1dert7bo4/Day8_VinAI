import json
import pandas as pd
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset
import os

def run_evaluation(pipeline_func, config_name, dataset_path="eval/golden_dataset.json"):
    print(f"\n--- Đang chạy evaluation cho config: {config_name} ---")
    
    # Load golden dataset
    with open(dataset_path, "r", encoding="utf-8") as f:
        golden_dataset = json.load(f)

    # Chuẩn bị data theo đúng format của RAGAS
    eval_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    print("Đang tạo câu trả lời cho các câu hỏi trong dataset...")
    # Chạy pipeline cho từng câu hỏi
    for item in golden_dataset:
        # Giả sử pipeline_func nhận câu hỏi và trả về dict có chứa 'answer' và 'sources'
        result = pipeline_func(item["question"])
        
        eval_data["question"].append(item["question"])
        eval_data["answer"].append(result["answer"])
        eval_data["contexts"].append([c["content"] for c in result.get("sources", [])])
        eval_data["ground_truth"].append(item["expected_answer"])

    dataset = Dataset.from_dict(eval_data)

    print("Đang chấm điểm bằng RAGAS...")
    # Chạy evaluation với ragas
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )
    
    df_results = result.to_pandas()
    print("Kết quả điểm trung bình:")
    print(df_results[["faithfulness", "answer_relevancy", "context_recall", "context_precision"]].mean())

    # Phân tích worst performers (ví dụ sort theo faithfulness thấp nhất)
    # Lọc ra top 3 câu có faithfulness thấp nhất
    worst_performers = df_results.sort_values(by="faithfulness").head(3)

    # Lưu kết quả bảng vào result.md
    result_file = "eval/result.md"
    # Đảm bảo thư mục tồn tại
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    
    with open(result_file, "a", encoding="utf-8") as f:
        f.write(f"\n## Kết quả Evaluation - Config: {config_name}\n\n")
        f.write("### Bảng điểm chi tiết\n\n")
        f.write(df_results.to_markdown(index=False))
        f.write("\n\n### Điểm trung bình\n\n")
        f.write(df_results[["faithfulness", "answer_relevancy", "context_recall", "context_precision"]].mean().to_markdown())
        f.write("\n\n### Phân tích Worst Performers (Faithfulness thấp nhất)\n\n")
        f.write(worst_performers[["question", "answer", "faithfulness", "ground_truth"]].to_markdown(index=False))
        f.write("\n\n---\n")

    return df_results

if __name__ == "__main__":
    # GIẢ LẬP: Để test script, mình tạo 2 hàm pipeline giả (bạn sẽ thay bằng hàm RAG thật của nhóm)
    def mock_pipeline_A(query):
        return {
            "answer": "Ca sĩ Chi Dân bị truy tố về tội tổ chức sử dụng trái phép chất ma túy.",
            "sources": [{"content": "Trong đó ca sĩ Chi Dân bị truy tố về tội tổ chức sử dụng trái phép chất ma túy."}]
        }
    
    def mock_pipeline_B(query):
        return {
            "answer": "Mình không tìm thấy thông tin Chi Dân bị tội gì.",
            "sources": [{"content": "Nhiều nghệ sĩ bị bắt."}]
        }

    # 1. Reset file result.md trước khi chạy
    with open("eval/result.md", "w", encoding="utf-8") as f:
        f.write("# Báo cáo kết quả RAG Evaluation\n\n")

    # 2. Chạy So sánh A/B
    # Mở comment và thay hàm dưới đây khi bạn đã có pipeline_func thực tế
    
    print("Bắt đầu chạy A/B testing...")
    results_A = run_evaluation(mock_pipeline_A, "Config A (Hybrid Search + Reranker)")
    results_B = run_evaluation(mock_pipeline_B, "Config B (Dense Only, No Reranker)")
    
    # 3. Bảng so sánh tổng hợp A/B
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
