# 🌾 Fasal Salahkaar (ਫ਼ਸਲ ਸਲਾਹਕਾਰ) — Crop Advisor

**Fasal Salahkaar** is a production-grade, multilingual agricultural AI assistant built for Punjab's farmers. It uses **Retrieval-Augmented Generation (RAG)** to answer farming questions by retrieving context from Punjabi agricultural documents and generating precise answers using the **Mistral LLM**.

> 🌐 **Supports**: Punjabi (ਪੰਜਾਬੀ) • Hindi (हिन्दी) • English

---

## ✨ Features

### 1. 💬 Conversational Memory
Multi-turn chat interface with session-based conversation history. The model understands follow-up questions like "ਇਸ ਬਾਰੇ ਹੋਰ ਦੱਸੋ" (tell me more about this).

### 2. 📊 RAG Evaluation Pipeline (RAGAS)
Standalone evaluation script that measures:
- **Faithfulness** — Does the answer stick to retrieved context?
- **Answer Relevancy** — Is the answer relevant to the question?
- **Context Precision** — Are retrieved chunks relevant?
- **Context Recall** — Did we retrieve enough relevant context?

### 3. 📚 Source Citations with Confidence Scores
Every answer shows expandable source cards with:
- Document name and chunk location
- Confidence percentage (0-100%) with color-coded bar
- Preview of the retrieved chunk text

### 4. 🌐 Multilingual Support
- **Punjabi** (ਪੰਜਾਬੀ) — Native language of the knowledge base
- **Hindi** (हिन्दी) — Cross-lingual response generation
- **English** — For wider accessibility

All retrieval happens in Punjabi; the LLM translates its response.

### 5. 📈 Query Analytics Dashboard
Real-time analytics with interactive Plotly charts:
- Total queries served
- Response time trends
- Confidence score distribution
- Language usage breakdown
- Recent query history

### 6. 🧠 Semantic Chunking
`RecursiveCharacterTextSplitter` with Punjabi-aware separators for smarter boundary detection. Rich metadata per chunk (file name, chunk index, size).

### 7. 🎨 Premium UI
Dark-themed glassmorphism design with:
- Gradient headers with Inter font
- Styled chat bubbles with avatars
- Animated typing indicator
- Card-based source citations
- Welcome screen with clickable example questions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                        │
│  (Chat Interface / Analytics Dashboard / Sidebar)       │
├──────────┬──────────────────────┬───────────────────────┤
│          │                      │                       │
│  Language │   Conversation      │    Analytics           │
│  Selector │   Memory            │    Logger             │
│          │   (Session State)    │    (JSON)             │
├──────────┴──────────────────────┴───────────────────────┤
│                    RAG Pipeline                         │
│  ┌─────────┐  ┌──────────┐  ┌────────────────────┐     │
│  │  FAISS  │→ │  Top-3   │→ │  Mistral LLM       │     │
│  │  Index  │  │  Chunks  │  │  + Chat History     │     │
│  │         │  │  + Scores │  │  + Language Prompt  │     │
│  └─────────┘  └──────────┘  └────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│              Punjabi SBERT Embeddings                   │
│         (l3cube-pune/punjabi-sentence-similarity)       │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
Punjabi-AgroBot/
├── app/
│   ├── app.py              ← Main Streamlit application
│   └── analytics.py        ← Query logging & analytics module
├── vectordb/               ← Punjabi agricultural .txt documents
│   ├── Citrus_Cultivation_pbi.txt
│   ├── pp_kharif_pbi.txt
│   ├── pp_rabi_pbi.txt
│   ├── pp_veg_pbi.txt
│   ├── pp_fruits_pbi.txt
│   └── FruitDropCitrusP.txt
├── build_faiss_index.py    ← FAISS index builder (semantic chunking)
├── evaluate_rag.py         ← RAG evaluation pipeline (RAGAS)
├── eval_dataset.json       ← Evaluation Q&A dataset (10 pairs)
├── requirements.txt        ← Python dependencies
├── .env                    ← API keys (not committed)
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Ishita-01/Fasla-Salahkaar.git
cd Punjabi-AgroBot
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key

Create a `.env` file in the root folder:

```
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 5. Prepare text files

Ensure `.txt` files containing Punjabi agricultural information are in the `vectordb/` folder.

### 6. Build the FAISS Index

```bash
python build_faiss_index.py
```

This will:
- Load the Punjabi SBERT embedding model
- Read all `.txt` files from `vectordb/`
- Chunk using `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap)
- Enrich metadata (file name, chunk index, file size)
- Print a **chunk quality report** with statistics
- Save the FAISS index to `faiss_index/phama_faiss/`

### 7. Run the application

```bash
streamlit run app/app.py
```

---

## Step-by-Step Workflow

### `build_faiss_index.py`

1. Load the **Punjabi SBERT embedding model** with CUDA support.
2. Read `.txt` files from `vectorDb/`.
3. Chunk each file into overlapping segments.
4. Store each chunk in a LangChain `Document` with metadata.
5. Create a FAISS vectorstore from all chunks.
6. Save the vectorstore to `faiss_index/agrobot_faiss/`.

### `app/app.py`

1. Load environment variables using `dotenv`.
2. Load the FAISS index and embedding model (cached for performance).
3. Define a Punjabi prompt using LangChain's `ChatPromptTemplate`.
4. Load the Mistral model (`mistral-large-latest`) for inference.
5. On user input:
   - Embed the query
   - Perform FAISS similarity search (top-3 chunks)
   - Format results as context
   - Generate a response using the LLM
6. Display the final Punjabi answer using Streamlit.

---

## 📊 Sample Chunk Quality Report

```
============================================================
📊 CHUNK QUALITY REPORT
============================================================
  Total files processed : 6
  Total chunks created  : 3847
  Avg chunk size        : 812 chars
  Min chunk size        : 23 chars
  Max chunk size        : 1000 chars
  Std deviation         : 245 chars

  Chunks per file:
    Citrus_Cultivation_pbi.txt              →   283 chunks  (   266,142 bytes)
    pp_kharif_pbi.txt                       →  1132 chunks  ( 1,086,294 bytes)
    pp_rabi_pbi.txt                         →  1019 chunks  (   977,632 bytes)
    ...
============================================================
```

---

## Note

- The chatbot only uses the **pre-built index**.
- If you add or update `.txt` files, rerun `build_faiss_index.py` to rebuild the index.

---

## GitHub

Project Repository: [https://github.com/WakeUpSidd/Punjabi-AgroBot](https://github.com/WakeUpSidd/Punjabi-AgroBot)
