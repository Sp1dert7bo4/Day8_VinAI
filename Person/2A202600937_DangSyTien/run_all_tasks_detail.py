import os
from src.task4_chunking_indexing import load_documents, chunk_documents
from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank
from src.task8_pageindex_vectorless import pageindex_search
from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import generate_with_citation

query = "hình phạt đối với tội phạm ma tuý"

print("\n" + "="*50)
print("TASK 4: Chunking & Indexing")
docs = load_documents()
chunks = chunk_documents(docs)
print(f"Loaded {len(docs)} documents. Generated {len(chunks)} chunks.")

print("\n" + "="*50)
print("TASK 5: Semantic Search")
sem_res = semantic_search(query, top_k=2)
for i, r in enumerate(sem_res):
    print(f"Result {i+1}: [Score: {r.get('score', 0):.4f}] {r['content'][:100]}...")

print("\n" + "="*50)
print("TASK 6: Lexical Search (BM25)")
lex_res = lexical_search(query, top_k=2)
for i, r in enumerate(lex_res):
    print(f"Result {i+1}: [Score: {r.get('score', 0):.4f}] {r['content'][:100]}...")

print("\n" + "="*50)
print("TASK 7: Reranking")
# Dùng kết quả của task 5 làm candidate
reranked = rerank(query, sem_res, top_k=2)
for i, r in enumerate(reranked):
    print(f"Result {i+1}: [Score: {r.get('score', 0):.4f}] {r['content'][:100]}...")

print("\n" + "="*50)
print("TASK 8: PageIndex (Vectorless Fallback)")
pi_res = pageindex_search(query, top_k=2)
for i, r in enumerate(pi_res):
    print(f"Result {i+1}: [Score: {r.get('score', 0):.4f}] {r['content'][:100]}...")

print("\n" + "="*50)
print("TASK 9: Retrieval Pipeline (Hybrid + Rerank)")
pipe_res = retrieve(query, top_k=2)
for i, r in enumerate(pipe_res):
    print(f"Result {i+1}: [Score: {r.get('score', 0):.4f}, Source: {r.get('source')}] {r['content'][:100]}...")

print("\n" + "="*50)
print("TASK 10: Generation with LLM")
final_ans = generate_with_citation(query)
print(final_ans.get("answer"))
