"""
Fasal Salahkaar — Query Analytics Module

Logs each user query and provides aggregation functions
for the analytics dashboard.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "query_logs"))
LOG_FILE = os.path.join(LOG_DIR, "queries.json")


# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────
def log_query(
    question: str,
    language: str,
    response_time: float,
    num_chunks: int,
    confidence_scores: list[float],
    answer_length: int,
) -> None:
    """Append a query record to the local JSON log file."""
    os.makedirs(LOG_DIR, exist_ok=True)

    record = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "language": language,
        "response_time_s": round(response_time, 3),
        "num_chunks": num_chunks,
        "confidence_scores": [round(s, 4) for s in confidence_scores],
        "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 4) if confidence_scores else 0.0,
        "answer_length": answer_length,
    }

    # Read existing logs, append, and write back (atomic for small files)
    logs = _read_logs()
    logs.append(record)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────────────────────────
# Reading
# ──────────────────────────────────────────────────────────────────────────────
def _read_logs() -> list[dict[str, Any]]:
    """Read the query log file and return a list of records."""
    if not os.path.isfile(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def get_all_logs() -> list[dict[str, Any]]:
    """Public accessor for all log records."""
    return _read_logs()


def get_summary_stats() -> dict[str, Any]:
    """Compute summary statistics from the logs."""
    logs = _read_logs()
    if not logs:
        return {
            "total_queries": 0,
            "avg_response_time": 0.0,
            "languages": {},
            "avg_confidence": 0.0,
        }

    total = len(logs)
    avg_rt = sum(r["response_time_s"] for r in logs) / total
    avg_conf = sum(r.get("avg_confidence", 0.0) for r in logs) / total

    lang_counts: dict[str, int] = {}
    for r in logs:
        lang = r.get("language", "Unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    return {
        "total_queries": total,
        "avg_response_time": round(avg_rt, 3),
        "languages": lang_counts,
        "avg_confidence": round(avg_conf, 4),
    }
