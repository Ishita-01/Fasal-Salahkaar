"""
ਫ਼ਸਲ ਸਲਾਹਕਾਰ (Fasal Salahkaar) — Crop Advisor
═══════════════════════════════════════════════════
A production-grade Punjabi agricultural AI assistant with:
  • Conversational memory (multi-turn chat)
  • Source citations with confidence scores
  • Multilingual support (Punjabi / Hindi / English)
  • Query analytics dashboard
  • Premium dark-themed UI
"""

import os
import time
import json

import streamlit as st
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# 0) Page Config (MUST be first Streamlit command)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ਫ਼ਸਲ ਸਲਾਹਕਾਰ | Fasal Salahkaar",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# 1) Premium CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Import Google Font ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ─────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main background ────────────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
}

/* ── Sidebar ────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1b2838 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e0e0 !important;
}

/* ── Header gradient ────────────────────────────────────────────────────── */
.header-gradient {
    background: linear-gradient(90deg, #00b4d8, #48cae4, #90e0ef);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.4rem;
    font-weight: 700;
    margin-bottom: 0;
    letter-spacing: -0.5px;
}
.header-sub {
    color: #8b95a5;
    font-size: 1rem;
    font-weight: 400;
    margin-top: 0;
}

/* ── Chat bubbles ───────────────────────────────────────────────────────── */
div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    backdrop-filter: blur(8px);
    transition: all 0.2s ease;
}
div[data-testid="stChatMessage"]:hover {
    border-color: rgba(0,180,216,0.2);
    box-shadow: 0 4px 20px rgba(0,180,216,0.05);
}

/* ── Source cards ────────────────────────────────────────────────────────── */
.source-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    transition: all 0.2s ease;
}
.source-card:hover {
    border-color: rgba(72,202,228,0.3);
    background: rgba(255,255,255,0.06);
    transform: translateY(-1px);
}
.source-title {
    color: #48cae4;
    font-weight: 600;
    font-size: 0.85rem;
}
.source-score {
    color: #90e0ef;
    font-size: 0.8rem;
    font-weight: 500;
}
.source-preview {
    color: #a0aab4;
    font-size: 0.78rem;
    line-height: 1.4;
    margin-top: 0.4rem;
}

/* ── Confidence bar ─────────────────────────────────────────────────────── */
.confidence-bar {
    height: 4px;
    border-radius: 2px;
    background: rgba(255,255,255,0.08);
    margin-top: 0.4rem;
    overflow: hidden;
}
.confidence-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.6s ease;
}

/* ── Welcome card ───────────────────────────────────────────────────────── */
.welcome-card {
    background: linear-gradient(135deg, rgba(0,180,216,0.08) 0%, rgba(144,224,239,0.04) 100%);
    border: 1px solid rgba(72,202,228,0.15);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 2rem auto;
    max-width: 700px;
}
.welcome-title {
    color: #48cae4;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.welcome-desc {
    color: #8b95a5;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* ── Example question buttons ───────────────────────────────────────────── */
.example-btn {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    color: #c8d6e5;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
    width: 100%;
    margin-bottom: 0.4rem;
}
.example-btn:hover {
    background: rgba(0,180,216,0.1);
    border-color: rgba(72,202,228,0.3);
    color: #48cae4;
}

/* ── Typing indicator ───────────────────────────────────────────────────── */
@keyframes typing-pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}
.typing-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #48cae4;
    margin: 0 3px;
    animation: typing-pulse 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

/* ── Stats card ─────────────────────────────────────────────────────────── */
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.stat-value {
    color: #48cae4;
    font-size: 1.6rem;
    font-weight: 700;
}
.stat-label {
    color: #8b95a5;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Hide default Streamlit elements for cleaner look ───────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ── Scrollbar styling ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
::-webkit-scrollbar-thumb { background: rgba(72,202,228,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(72,202,228,0.5); }

/* ── Override text input colors ─────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea {
    color: #e0e0e0 !important;
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.1) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# 2) Load environment
# ──────────────────────────────────────────────────────────────────────────────
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", None)

# ──────────────────────────────────────────────────────────────────────────────
# 3) Language configuration
# ──────────────────────────────────────────────────────────────────────────────
LANG_CONFIG = {
    "ਪੰਜਾਬੀ": {
        "code": "pa",
        "chat_placeholder": "ਆਪਣਾ ਸਵਾਲ ਇੱਥੇ ਲਿਖੋ...",
        "thinking": "ਸੋਚ ਰਿਹਾ ਹਾਂ",
        "sources_title": "📚 ਸਰੋਤ ਅਤੇ ਭਰੋਸੇ ਦੇ ਅੰਕ",
        "clear_chat": "🗑️ ਗੱਲਬਾਤ ਮਿਟਾਓ",
        "welcome_title": "ਫ਼ਸਲ ਸਲਾਹਕਾਰ ਵਿੱਚ ਜੀ ਆਇਆਂ ਨੂੰ!",
        "welcome_desc": "ਮੈਂ ਤੁਹਾਡਾ ਖੇਤੀ ਸਹਾਇਕ ਹਾਂ। ਮੈਨੂੰ ਕੋਈ ਵੀ ਖੇਤੀ ਸੰਬੰਧੀ ਸਵਾਲ ਪੁੱਛੋ।",
        "response_time": "ਜਵਾਬ ਦਾ ਸਮਾਂ",
        "confidence": "ਭਰੋਸਾ",
        "source": "ਸਰੋਤ",
        "analytics_title": "📊 ਵਿਸ਼ਲੇਸ਼ਣ",
        "system_prompt": """ਤੁਸੀਂ ਫ਼ਸਲ ਸਲਾਹਕਾਰ ਹੋ — ਪੰਜਾਬ ਦੇ ਕਿਸਾਨਾਂ ਲਈ ਇੱਕ ਖੇਤੀ AI ਸਹਾਇਕ।
ਆਪਣੇ ਗਿਆਨ ਅਤੇ ਹੇਠਾਂ ਦਿੱਤੇ ਸੰਦਰਭਾਂ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਸਵਾਲ ਦਾ ਪੰਜਾਬੀ ਵਿੱਚ ਸੰਯੁਕਤ ਜਵਾਬ ਦਿਓ।

{history_section}

ਸੰਦਰਭ:
{context}""",
    },
    "हिन्दी": {
        "code": "hi",
        "chat_placeholder": "अपना सवाल यहाँ लिखें...",
        "thinking": "सोच रहा हूँ",
        "sources_title": "📚 स्रोत और विश्वास अंक",
        "clear_chat": "🗑️ चैट मिटाएँ",
        "welcome_title": "फ़सल सलाहकार में आपका स्वागत है!",
        "welcome_desc": "मैं आपका कृषि सहायक हूँ। मुझसे कोई भी खेती से जुड़ा सवाल पूछें।",
        "response_time": "जवाब का समय",
        "confidence": "विश्वास",
        "source": "स्रोत",
        "analytics_title": "📊 विश्लेषण",
        "system_prompt": """आप फ़सल सलाहकार हैं — पंजाब के किसानों के लिए एक कृषि AI सहायक।
अपने ज्ञान और नीचे दिए गए संदर्भों का उपयोग करके सवाल का हिन्दी में उत्तर दें।
ध्यान दें: संदर्भ पंजाबी में हैं, लेकिन आपको हिन्दी में जवाब देना है।

{history_section}

संदर्भ:
{context}""",
    },
    "English": {
        "code": "en",
        "chat_placeholder": "Type your question here...",
        "thinking": "Thinking",
        "sources_title": "📚 Sources & Confidence Scores",
        "clear_chat": "🗑️ Clear Chat",
        "welcome_title": "Welcome to Fasal Salahkaar!",
        "welcome_desc": "I'm your agricultural assistant. Ask me any farming-related question.",
        "response_time": "Response time",
        "confidence": "Confidence",
        "source": "Source",
        "analytics_title": "📊 Analytics",
        "system_prompt": """You are Fasal Salahkaar — an agricultural AI assistant for Punjab farmers.
Use your knowledge and the contexts below to answer the question in English.
Note: The contexts are in Punjabi, but you must respond in English.

{history_section}

Context:
{context}""",
    },
}

EXAMPLE_QUESTIONS = {
    "ਪੰਜਾਬੀ": [
        "ਕਿੰਨੂ ਦੀ ਖੇਤੀ ਲਈ ਕਿਹੜੀ ਮਿੱਟੀ ਢੁੱਕਵੀਂ ਹੈ?",
        "ਝੋਨੇ ਦੀ ਪਨੀਰੀ ਕਦੋਂ ਬੀਜੀਏ?",
        "ਕਣਕ ਵਿੱਚ ਕੁੰਗੀ ਦੀ ਰੋਕਥਾਮ ਕਿਵੇਂ ਕਰੀਏ?",
        "ਨਰਮੇ ਦੀ ਗੁਲਾਬੀ ਸੁੰਡੀ ਬਾਰੇ ਦੱਸੋ",
    ],
    "हिन्दी": [
        "किन्नू की खेती के लिए कौन सी मिट्टी उपयुक्त है?",
        "धान की पौध कब बोएं?",
        "गेहूं में जंग की रोकथाम कैसे करें?",
        "कपास की गुलाबी सुंडी के बारे में बताएं",
    ],
    "English": [
        "What soil is suitable for Kinnow cultivation?",
        "When to sow rice nursery?",
        "How to prevent rust in wheat?",
        "Tell me about pink bollworm in cotton",
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# 4) Load vectorstore (cached)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🔄 ਫ਼ੈਸਲ ਇੰਡੈਕਸ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...")
def load_vectorstore():
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    EMBED_MODEL = "l3cube-pune/punjabi-sentence-similarity-sbert"
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
    )

    INDEX_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "faiss_index", "phama_faiss")
    )

    if not os.path.isdir(INDEX_DIR):
        st.error(
            "❌ FAISS index not found! Run `python build_faiss_index.py` first."
        )
        return None

    vectorstore = FAISS.load_local(
        INDEX_DIR, embeddings, allow_dangerous_deserialization=True
    )
    return vectorstore


@st.cache_resource(show_spinner="🤖 LLM ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...")
def init_llm():
    from langchain_mistralai import ChatMistralAI

    return ChatMistralAI(model="mistral-large-latest", temperature=0)


vectorstore = load_vectorstore()
if vectorstore is None:
    st.stop()

llm_obj = init_llm()


# ──────────────────────────────────────────────────────────────────────────────
# 5) Helper: RAG pipeline with source attribution
# ──────────────────────────────────────────────────────────────────────────────
def get_answer_with_sources(question: str, language: str, chat_history: list):
    """Retrieve, generate, and return answer + sources with confidence scores."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableMap
    from langchain_core.output_parsers import StrOutputParser

    # 1) Condense follow-up question if history exists
    search_query = question
    if chat_history:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # Format history for prompt
        history_lines = []
        for msg in chat_history[-6:]:  # last 3 turns
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['content'][:300]}")
        history_str = "\n".join(history_lines)

        condense_prompt = ChatPromptTemplate.from_messages([
            ("system", """Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question (in the same language as the follow-up question) that can be understood without the conversation history. Do NOT answer the question, just reformulate it.

Conversation History:
{history}"""),
            ("human", "Follow-up Question: {question}")
        ])

        condense_chain = condense_prompt | llm_obj | StrOutputParser()
        try:
            condensed = condense_chain.invoke({"history": history_str, "question": question})
            search_query = condensed.strip()
        except Exception:
            pass

    # 2) Translate search query to Punjabi if not already Punjabi to ensure high retrieval accuracy on the Punjabi database
    retrieval_query = search_query
    if language != "ਪੰਜਾਬੀ":
        translation_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert translator. Translate the following user agricultural query from Hindi or English into Punjabi. Output ONLY the translated Punjabi question, nothing else. Do not add any explanation, notes, or markdown formatting."),
            ("human", "{question}")
        ])
        translation_chain = translation_prompt | llm_obj | StrOutputParser()
        try:
            translated = translation_chain.invoke({"question": search_query})
            retrieval_query = translated.strip()
        except Exception:
            pass

    # 3) Retrieve with scores using retrieval query in Punjabi
    docs_with_scores = vectorstore.similarity_search_with_score(retrieval_query, k=3)

    # 2) Format contexts
    formatted_contexts = "\n\n".join(
        [
            f"ਸੰਦਰਭ {i+1} ({doc.metadata.get('file_name', doc.metadata.get('source', 'Unknown'))}): {doc.page_content}"
            for i, (doc, _) in enumerate(docs_with_scores)
        ]
    )

    # 3) Build conversation history section
    history_section = ""
    if chat_history:
        recent = chat_history[-6:]  # last 3 turns (6 messages)
        history_lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['content'][:300]}")
        history_section = "Previous conversation:\n" + "\n".join(history_lines)

    # 4) Build prompt
    lang_cfg = LANG_CONFIG[language]
    system_text = lang_cfg["system_prompt"].format(
        context=formatted_contexts,
        history_section=history_section,
    )

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_text), ("human", "{question}")]
    )

    # 5) Run chain
    rag_chain = (
        RunnableMap({"question": lambda _: question})
        | prompt
        | llm_obj
        | StrOutputParser()
    )

    stream_generator = rag_chain.stream({})

    # 6) Process sources
    sources = []
    for doc, score in docs_with_scores:
        # FAISS returns L2 distance; convert to confidence
        # Lower score = more similar. Using exponential decay for nicer %
        import math
        confidence = math.exp(-score / 2) * 100  # rough conversion
        confidence = min(confidence, 99.9)

        sources.append(
            {
                "file_name": doc.metadata.get("file_name", doc.metadata.get("source", "Unknown")),
                "chunk_id": doc.metadata.get("source", ""),
                "chunk_index": doc.metadata.get("chunk_index", "?"),
                "total_chunks": doc.metadata.get("total_chunks", "?"),
                "confidence": round(confidence, 1),
                "preview": doc.page_content[:200],
                "raw_score": float(score),
            }
        )

    return stream_generator, sources


# ──────────────────────────────────────────────────────────────────────────────
# 6) Session state initialization
# ──────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "ਪੰਜਾਬੀ"
if "page" not in st.session_state:
    st.session_state.page = "chat"


# ──────────────────────────────────────────────────────────────────────────────
# 7) Sidebar
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="header-gradient" style="font-size:1.6rem;">🌾 ਫ਼ਸਲ ਸਲਾਹਕਾਰ</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b95a5; font-size:0.85rem; margin-top:-10px;">Crop Advisor • ਫ਼ਸਲ ਸਲਾਹਕਾਰ</p>', unsafe_allow_html=True)
    st.divider()

    # Language selector
    st.markdown("##### 🌐 Language / ਭਾਸ਼ਾ")
    selected_lang = st.selectbox(
        "Select language",
        options=list(LANG_CONFIG.keys()),
        index=list(LANG_CONFIG.keys()).index(st.session_state.language),
        label_visibility="collapsed",
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

    lang_cfg = LANG_CONFIG[st.session_state.language]

    st.divider()

    # Page navigation
    st.markdown("##### 📑 Navigation")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
            st.session_state.page = "chat"
            st.rerun()
    with col2:
        if st.button("📊 Analytics", use_container_width=True, type="primary" if st.session_state.page == "analytics" else "secondary"):
            st.session_state.page = "analytics"
            st.rerun()

    st.divider()

    # Clear chat
    if st.button(lang_cfg["clear_chat"], use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # About section
    st.markdown("##### ℹ️ About")
    st.markdown(
        """
        <div style="color:#8b95a5; font-size:0.78rem; line-height:1.6;">
        <b>Model:</b> Mistral Large<br>
        <b>Embeddings:</b> Punjabi SBERT<br>
        <b>Knowledge:</b> PAU Agricultural Guides<br>
        <b>Retrieval:</b> FAISS (Top-3)<br>
        <br>
        Built with ❤️ for Punjab's farmers
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 8) Analytics Page
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "analytics":
    st.markdown(f'<p class="header-gradient">{lang_cfg["analytics_title"]}</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Query insights and performance metrics</p>', unsafe_allow_html=True)
    st.markdown("")

    try:
        from analytics import get_all_logs, get_summary_stats

        stats = get_summary_stats()
        logs = get_all_logs()

        if stats["total_queries"] == 0:
            st.info("📭 No queries logged yet. Start chatting to see analytics!")
            st.stop()

        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{stats['total_queries']}</div>
                    <div class="stat-label">Total Queries</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{stats['avg_response_time']}s</div>
                    <div class="stat-label">Avg Response Time</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{stats['avg_confidence']:.1%}</div>
                    <div class="stat-label">Avg Confidence</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col4:
            langs_str = ", ".join(f"{k}: {v}" for k, v in stats["languages"].items())
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-value">{len(stats['languages'])}</div>
                    <div class="stat-label">Languages Used</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("")

        # Charts
        import plotly.express as px
        import plotly.graph_objects as go

        col1, col2 = st.columns(2)

        with col1:
            # Response time chart
            times = [r["response_time_s"] for r in logs]
            fig_rt = go.Figure()
            fig_rt.add_trace(
                go.Scatter(
                    y=times,
                    mode="lines+markers",
                    line=dict(color="#48cae4", width=2),
                    marker=dict(size=6, color="#48cae4"),
                    fill="tozeroy",
                    fillcolor="rgba(72,202,228,0.1)",
                )
            )
            fig_rt.update_layout(
                title="Response Time Trend",
                xaxis_title="Query #",
                yaxis_title="Time (s)",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
                margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig_rt, use_container_width=True)

        with col2:
            # Language distribution
            if stats["languages"]:
                fig_lang = px.pie(
                    names=list(stats["languages"].keys()),
                    values=list(stats["languages"].values()),
                    title="Language Distribution",
                    color_discrete_sequence=["#48cae4", "#90e0ef", "#00b4d8"],
                )
                fig_lang.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=300,
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                st.plotly_chart(fig_lang, use_container_width=True)

        # Confidence distribution
        confidences = [r.get("avg_confidence", 0) for r in logs]
        if confidences:
            fig_conf = go.Figure()
            fig_conf.add_trace(
                go.Histogram(
                    x=confidences,
                    nbinsx=20,
                    marker_color="#48cae4",
                    opacity=0.7,
                )
            )
            fig_conf.update_layout(
                title="Confidence Score Distribution",
                xaxis_title="Confidence",
                yaxis_title="Count",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=280,
                margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig_conf, use_container_width=True)

        # Recent queries table
        st.markdown("##### 📝 Recent Queries")
        recent = logs[-10:][::-1]
        for r in recent:
            ts = r.get("timestamp", "")[:16].replace("T", " ")
            st.markdown(
                f"""<div class="source-card">
                    <span class="source-title">{r.get('question', '')[:80]}</span><br>
                    <span class="source-score">{ts} • {r.get('language', '')} • {r.get('response_time_s', 0)}s • Confidence: {r.get('avg_confidence', 0):.1%}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    except ImportError:
        st.error("Analytics module not found.")
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# 9) Chat Page — Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="header-gradient">🌾 ਫ਼ਸਲ ਸਲਾਹਕਾਰ</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="header-sub">Fasal Salahkaar — Your AI Crop Advisor powered by Punjab Agricultural University knowledge</p>',
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# 10) Welcome screen (when no messages)
# ──────────────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        f"""<div class="welcome-card">
            <div class="welcome-title">🌾 {lang_cfg['welcome_title']}</div>
            <div class="welcome-desc">{lang_cfg['welcome_desc']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Example questions
    st.markdown(f"##### 💡 {'ਉਦਾਹਰਨ ਸਵਾਲ' if st.session_state.language == 'ਪੰਜਾਬੀ' else 'उदाहरण प्रश्न' if st.session_state.language == 'हिन्दी' else 'Example Questions'}")
    examples = EXAMPLE_QUESTIONS.get(st.session_state.language, EXAMPLE_QUESTIONS["ਪੰਜਾਬੀ"])

    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"💬 {ex}", key=f"ex_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": ex})
                st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# 11) Display chat history
# ──────────────────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🧑‍🌾" if msg["role"] == "user" else "🌾"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


        if "response_time" in msg:
            st.caption(f"⏱️ {lang_cfg['response_time']}: {msg['response_time']:.2f}s")


# ──────────────────────────────────────────────────────────────────────────────
# 12) Chat input
# ──────────────────────────────────────────────────────────────────────────────
if user_input := st.chat_input(lang_cfg["chat_placeholder"]):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# 13) Generate response if last message is from user
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_message = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant", avatar="🌾"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<div style="padding:0.5rem 0;"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>',
            unsafe_allow_html=True,
        )

        start_time = time.time()
        try:
            stream_generator, sources = get_answer_with_sources(
                last_user_message,
                st.session_state.language,
                st.session_state.messages[:-1],  # exclude current user msg
            )
            # Clear typing indicator
            typing_placeholder.empty()
            # Stream response to UI
            answer = st.write_stream(stream_generator)
        except Exception as e:
            typing_placeholder.empty()
            answer = f"🚨 Error: {e}"
            sources = []

        elapsed = time.time() - start_time

        st.caption(f"⏱️ {lang_cfg['response_time']}: {elapsed:.2f}s")

    # Store assistant message with metadata
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "response_time": elapsed,
        }
    )

    # Log to analytics
    try:
        from analytics import log_query

        confidence_scores = [s["confidence"] / 100 for s in sources]
        log_query(
            question=last_user_message,
            language=st.session_state.language,
            response_time=elapsed,
            num_chunks=len(sources),
            confidence_scores=confidence_scores,
            answer_length=len(answer),
        )
    except Exception:
        pass  # Analytics logging is non-critical

    st.rerun()



