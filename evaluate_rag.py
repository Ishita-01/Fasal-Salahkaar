"""
Fasal Salahkaar — RAG Evaluation Pipeline (LLM-as-a-Judge)

Runs the RAG pipeline over the evaluation dataset, evaluates the results
using Mistral LLM as an evaluator across key metrics:
  1. Faithfulness (Groundedness)
  2. Answer Relevancy
  3. Context Recall
Generates a detailed markdown report and a JSON results file.
"""

import os
import sys
import json
import time
import math
from datetime import datetime
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", None)

if not MISTRAL_API_KEY:
    print("❌ ERROR: MISTRAL_API_KEY not found in environment. Please check your .env file.")
    sys.exit(1)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser

# ──────────────────────────────────────────────────────────────────────────────
# 1) Load Vectorstore & Initialize Mistral
# ──────────────────────────────────────────────────────────────────────────────
print("🔄 Loading embeddings and FAISS index...")
EMBED_MODEL = "l3cube-pune/punjabi-sentence-similarity-sbert"
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
)

INDEX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "faiss_index", "phama_faiss"))
if not os.path.isdir(INDEX_DIR):
    print(f"❌ ERROR: FAISS index not found at {INDEX_DIR}. Run build_faiss_index.py first.")
    sys.exit(1)

vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)

# Initialize Mistral LLM for RAG & Evaluation
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

# RAG prompt
rag_system_prompt = """ਤੁਸੀਂ ਫ਼ਸਲ ਸਲਾਹਕਾਰ ਹੋ — ਪੰਜਾਬ ਦੇ ਕਿਸਾਨਾਂ ਲਈ ਇੱਕ ਖੇਤੀ AI ਸਹਾਇਕ।
ਆਪਣੇ ਗਿਆਨ ਅਤੇ ਹੇਠਾਂ ਦਿੱਤੇ ਸੰਦਰਭਾਂ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਸਵਾਲ ਦਾ ਪੰਜਾਬੀ ਵਿੱਚ ਸੰਯੁਕਤ ਜਵਾਬ ਦਿਓ।

ਸੰਦਰਭ:
{context}"""

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", rag_system_prompt),
    ("human", "{question}")
])

# ──────────────────────────────────────────────────────────────────────────────
# 2) Evaluator Prompts (LLM-as-a-Judge)
# ──────────────────────────────────────────────────────────────────────────────
# Faithfulness: Check if answer is derived ONLY from the context
faithfulness_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI quality auditor. Your task is to evaluate the Faithfulness (groundedness) of a generated answer compared to the retrieved context.
Faithfulness measures if the generated answer contains only claims that are directly supported by the retrieved context.

Evaluate the generated answer against the retrieved context:
- If all statements in the answer are supported by the context, the score should be close to 1.0.
- If there are statements not mentioned in the context (hallucinations), the score should be lower.

You must respond with a JSON object containing:
1. "score": a float between 0.0 and 1.0.
2. "reason": a brief, clear explanation of your rating.

Response format:
{{
  "score": <float>,
  "reason": "<explanation>"
}}
Do NOT output any other text or code blocks. Output raw JSON only."""),
    ("human", "Retrieved Context:\n{context}\n\nGenerated Answer:\n{answer}")
])

# Answer Relevancy: Check if answer addresses the query directly
relevancy_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI quality auditor. Your task is to evaluate the Answer Relevancy of a generated answer compared to the user's question.
Answer Relevancy measures how directly and completely the generated answer addresses the question. It ignores whether the answer is factually correct; it only checks if the response is on-topic and addresses all parts of the question.

You must respond with a JSON object containing:
1. "score": a float between 0.0 and 1.0.
2. "reason": a brief, clear explanation of your rating.

Response format:
{{
  "score": <float>,
  "reason": "<explanation>"
}}
Do NOT output any other text or code blocks. Output raw JSON only."""),
    ("human", "Question:\n{question}\n\nGenerated Answer:\n{answer}")
])

# Context Recall: Check if context contains the ground truth
recall_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI quality auditor. Your task is to evaluate the Context Recall of retrieved context compared to a ground truth answer.
Context Recall measures if the retrieved context contains all the necessary information to construct the ground truth answer.

Evaluate the retrieved context against the ground truth:
- If all key facts in the ground truth are present in the context, the score should be 1.0.
- If key facts are missing, the score should be lower.

You must respond with a JSON object containing:
1. "score": a float between 0.0 and 1.0.
2. "reason": a brief, clear explanation of your rating.

Response format:
{{
  "score": <float>,
  "reason": "<explanation>"
}}
Do NOT output any other text or code blocks. Output raw JSON only."""),
    ("human", "Ground Truth Answer:\n{ground_truth}\n\nRetrieved Context:\n{context}")
])

eval_parser = JsonOutputParser()

# Helper function to run evaluation
def invoke_with_retry(chain, inputs, max_retries=6, initial_delay=4):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower() or "limit" in err_str.lower():
                print(f"   ⚠️ Rate limited (429). Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise e
    raise RuntimeError("Failed to invoke chain after maximum retries due to rate limits.")

def run_eval_chain(prompt_template, inputs):
    chain = prompt_template | llm | eval_parser
    try:
        res = invoke_with_retry(chain, inputs)
        return res.get("score", 0.0), res.get("reason", "N/A")
    except Exception as e:
        # Fallback in case of JSON parsing issues
        print(f"⚠️ Warning: Eval parse failed: {e}. Retrying with string fallback...")
        fallback_chain = prompt_template | llm | StrOutputParser()
        try:
            txt = invoke_with_retry(fallback_chain, inputs)
            # Try parsing JSON manually if LLM wrapped it in markdown
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt:
                txt = txt.split("```")[1].split("```")[0].strip()
            data = json.loads(txt.strip())
            return data.get("score", 0.0), data.get("reason", "N/A")
        except Exception as ex:
            return 0.0, f"Error: {ex}"

# ──────────────────────────────────────────────────────────────────────────────
# 3) Run Evaluation Loop
# ──────────────────────────────────────────────────────────────────────────────
dataset_path = "eval_dataset.json"
if not os.path.isfile(dataset_path):
    print(f"❌ ERROR: Evaluation dataset not found at {dataset_path}.")
    sys.exit(1)

with open(dataset_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"📋 Loaded {len(dataset)} evaluation Q&A pairs. Starting evaluation...\n")

results = []
metrics_summary = {
    "faithfulness": [],
    "relevancy": [],
    "recall": [],
    "latency": []
}

for idx, item in enumerate(dataset):
    qid = item["id"]
    question = item["question"]
    ground_truth = item["ground_truth"]
    
    print(f"👉 [{idx+1}/{len(dataset)}] Evaluating QID: {qid}...")
    
    # RAG Execution
    start_time = time.time()
    
    # 1. Retrieve
    docs_with_scores = vectorstore.similarity_search_with_score(question, k=3)
    formatted_contexts = "\n\n".join([
        f"ਸੰਦਰਭ {i+1} ({doc.metadata.get('file_name', doc.metadata.get('source', 'Unknown'))}): {doc.page_content}"
        for i, (doc, _) in enumerate(docs_with_scores)
    ])
    
    # 2. Generate
    time.sleep(2)  # rate limiting delay
    rag_chain = (
        RunnableMap({"question": lambda _: question, "context": lambda _: formatted_contexts})
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    answer = invoke_with_retry(rag_chain, {})
    elapsed = time.time() - start_time
    
    print(f"   ⏱️ Response generated in {elapsed:.2f}s")
    
    # LLM-as-a-Judge Evaluation
    # 1. Faithfulness
    time.sleep(2)  # rate limiting delay
    f_score, f_reason = run_eval_chain(
        faithfulness_prompt, 
        {"context": formatted_contexts, "answer": answer}
    )
    
    # 2. Answer Relevancy
    time.sleep(2)  # rate limiting delay
    r_score, r_reason = run_eval_chain(
        relevancy_prompt, 
        {"question": question, "answer": answer}
    )
    
    # 3. Context Recall
    time.sleep(2)  # rate limiting delay
    rec_score, rec_reason = run_eval_chain(
        recall_prompt, 
        {"ground_truth": ground_truth, "context": formatted_contexts}
    )
    
    print(f"   📊 Scores -> Faithfulness: {f_score:.2f} | Relevancy: {r_score:.2f} | Recall: {rec_score:.2f}")
    
    # Save statistics
    metrics_summary["faithfulness"].append(f_score)
    metrics_summary["relevancy"].append(r_score)
    metrics_summary["recall"].append(rec_score)
    metrics_summary["latency"].append(elapsed)
    
    results.append({
        "id": qid,
        "question": question,
        "ground_truth": ground_truth,
        "retrieved_context": formatted_contexts,
        "generated_answer": answer,
        "latency_s": round(elapsed, 3),
        "scores": {
            "faithfulness": f_score,
            "relevancy": r_score,
            "recall": rec_score
        },
        "reasons": {
            "faithfulness": f_reason,
            "relevancy": r_reason,
            "recall": rec_reason
        }
    })

# ──────────────────────────────────────────────────────────────────────────────
# 4) Calculate Aggregates & Save Reports
# ──────────────────────────────────────────────────────────────────────────────
total_evals = len(results)
avg_faithfulness = sum(metrics_summary["faithfulness"]) / total_evals
avg_relevancy = sum(metrics_summary["relevancy"]) / total_evals
avg_recall = sum(metrics_summary["recall"]) / total_evals
avg_latency = sum(metrics_summary["latency"]) / total_evals

print("\n" + "="*50)
print("📊 EVALUATION RESULTS SUMMARY")
print("="*50)
print(f"  Total Q&A pairs evaluated : {total_evals}")
print(f"  Average Faithfulness      : {avg_faithfulness:.4f}")
print(f"  Average Answer Relevancy  : {avg_relevancy:.4f}")
print(f"  Average Context Recall    : {avg_recall:.4f}")
print(f"  Average Response Time     : {avg_latency:.2f}s")
print("="*50 + "\n")

# Create output folder
os.makedirs("evaluation_results", exist_ok=True)

# Save raw results JSON
results_json_path = os.path.join("evaluation_results", "results.json")
with open(results_json_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_queries": total_evals,
            "avg_faithfulness": round(avg_faithfulness, 4),
            "avg_relevancy": round(avg_relevancy, 4),
            "avg_recall": round(avg_recall, 4),
            "avg_response_time_s": round(avg_latency, 3)
        },
        "details": results
    }, f, ensure_ascii=False, indent=2)

# Save Report Markdown
report_md_path = os.path.join("evaluation_results", "report.md")
with open(report_md_path, "w", encoding="utf-8") as f:
    f.write(f"""# 📊 Fasal Salahkaar — RAG Evaluation Report
Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This report summarizes the performance of the **Fasal Salahkaar** RAG chatbot evaluated over {total_evals} Punjabi agricultural Q&A pairs using LLM-as-a-Judge (Mistral Large).

## 📈 Executive Summary

| Metric | Score | Target | Interpretation |
| :--- | :---: | :---: | :--- |
| **Faithfulness** | `{avg_faithfulness:.2%}` | `> 80%` | Does the answer contain only facts supported by retrieved contexts? |
| **Answer Relevancy** | `{avg_relevancy:.2%}` | `> 80%` | Does the response directly address the user's question? |
| **Context Recall** | `{avg_recall:.2%}` | `> 70%` | Did the retrieval step fetch the necessary info from the database? |
| **Avg Latency** | `{avg_latency:.2f}s` | `< 5.0s` | Average end-to-end response generation speed. |

---

## 🔍 Detailed Q&A Evaluation Results

""")
    
    for r in results:
        f.write(f"""### Question QID: `{r['id']}`
**Question:** `{r['question']}`

**Ground Truth:**
> {r['ground_truth']}

**Generated Answer:**
> {r['generated_answer']}

**Metrics:**
* **Faithfulness:** `{r['scores']['faithfulness']:.2f}` — *{r['reasons']['faithfulness']}*
* **Answer Relevancy:** `{r['scores']['relevancy']:.2f}` — *{r['reasons']['relevancy']}*
* **Context Recall:** `{r['scores']['recall']:.2f}` — *{r['reasons']['recall']}*
* **Latency:** `{r['latency_s']:.2f}s`

---
""")

print(f"✅ Evaluation complete. Raw JSON saved to: {results_json_path}")
print(f"✅ Markdown report generated at: {report_md_path}")
