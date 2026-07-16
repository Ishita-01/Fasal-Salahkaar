"""
Fasal Salahkaar — FAISS Index Builder (Improved Chunking)

Uses RecursiveCharacterTextSplitter for smarter boundary detection,
enriches metadata, and prints a chunk quality report after indexing.
"""

import os
import sys
import glob
import statistics

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Force CPU (avoids CUDA errors on machines without GPU)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# ──────────────────────────────────────────────────────────────────────────────
# 1) Configuration
# ──────────────────────────────────────────────────────────────────────────────
EMBED_MODEL = "l3cube-pune/punjabi-sentence-similarity-sbert"
VECTORSTORE_DIR = "faiss_index"
VECTORSTORE_NAME = "phama_faiss"

# 2) Load SBERT embeddings (specialized Punjabi model for high retrieval accuracy)
print(f"Loading embedding model: {EMBED_MODEL}")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
)

# ──────────────────────────────────────────────────────────────────────────────
# 3) Read & chunk all .txt files with RecursiveCharacterTextSplitter
# ──────────────────────────────────────────────────────────────────────────────
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "vectordb"))
pattern = os.path.join(base_dir, "*.txt")
filepaths = glob.glob(pattern)

if not filepaths:
    raise RuntimeError(f"No .txt files found under {base_dir}")

# RecursiveCharacterTextSplitter tries multiple separators in order,
# providing smarter boundary detection than CharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "।", ".", " ", ""],
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

docs: list[Document] = []
file_stats: list[dict] = []

for fp in filepaths:
    file_name = os.path.basename(fp)
    file_size = os.path.getsize(fp)

    with open(fp, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        continue

    chunks = splitter.split_text(text)
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        chunk_id = f"{file_name}__chunk_{idx + 1}"
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "source": chunk_id,
                    "file_name": file_name,
                    "file_size": file_size,
                    "chunk_index": idx + 1,
                    "total_chunks": total_chunks,
                    "chunk_length": len(chunk),
                },
            )
        )

    file_stats.append(
        {
            "file_name": file_name,
            "file_size": file_size,
            "num_chunks": total_chunks,
        }
    )

# ──────────────────────────────────────────────────────────────────────────────
# 4) Chunk Quality Report
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("📊 CHUNK QUALITY REPORT")
print("=" * 60)

chunk_sizes = [d.metadata["chunk_length"] for d in docs]
print(f"  Total files processed : {len(file_stats)}")
print(f"  Total chunks created  : {len(docs)}")
print(f"  Avg chunk size        : {statistics.mean(chunk_sizes):.0f} chars")
print(f"  Min chunk size        : {min(chunk_sizes)} chars")
print(f"  Max chunk size        : {max(chunk_sizes)} chars")
print(f"  Std deviation         : {statistics.stdev(chunk_sizes):.0f} chars" if len(chunk_sizes) > 1 else "")
print()

print("  Chunks per file:")
for fs in file_stats:
    print(f"    {fs['file_name']:40s}  →  {fs['num_chunks']:>4d} chunks  ({fs['file_size']:>10,d} bytes)")

print("=" * 60 + "\n")

# ──────────────────────────────────────────────────────────────────────────────
# 5) Build FAISS index
# ──────────────────────────────────────────────────────────────────────────────
print(f"Building FAISS index from {len(docs)} chunks ...")
vectorstore = FAISS.from_documents(docs, embeddings)
print("Done building index.")

# ──────────────────────────────────────────────────────────────────────────────
# 6) Save the FAISS index to disk
# ──────────────────────────────────────────────────────────────────────────────
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
save_path = os.path.join(VECTORSTORE_DIR, VECTORSTORE_NAME)
print(f"Saving FAISS index to {save_path} ...")
vectorstore.save_local(save_path)
print("✅ Index saved successfully.")
