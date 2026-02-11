"""
MedGemma API client.

MedGemma is a self-hosted specialized Small Language Model fine-tuned on medical
literature. It performs:
  - NER (Named Entity Recognition): Extracts symptoms missing from charts.
  - Sentiment/History Analysis: Detects family history or lifestyle risks.

Returns: { "answer": "...", "citations": [...] }
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

# Timeout: 30s connect, 120s read (LLM inference can be quite slow)
_TIMEOUT = httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)


class MedGemmaResponse:
    """Parsed MedGemma result."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.answer: str = raw.get("answer", "")
        self.citations: list[str] = raw.get("citations", [])

    def __repr__(self) -> str:
        return f"MedGemmaResponse(answer_len={len(self.answer)}, citations={len(self.citations)})"


async def analyze(query: str) -> MedGemmaResponse:
    """
    Send free-text clinical data to MedGemma for NER + history analysis.

    Args:
        query: Combined clinical summary + symptoms text.
              e.g. "Patient presents with persistent AF... Clinical summary: ..."

    Returns:
        MedGemmaResponse with extracted answer and citations.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses after retry.
        httpx.TimeoutException: On timeout after retry.
    """
    payload = {
        "query": query,
        "top_k": 5,
        "include_answer": True,
        "model": "qwen/qwen3-32b",
    }
    max_retries = 1

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                logger.info(
                    "MedGemma request (attempt %d): %s", attempt + 1, settings.medgemma_url
                )
                response = await client.post(settings.medgemma_url, json=payload)
                response.raise_for_status()

                data = response.json()
                logger.info("MedGemma response received: answer_len=%d", len(data.get("answer", "")))
                return MedGemmaResponse(data)

        except (httpx.HTTPStatusError, httpx.TimeoutException) as exc:
            if attempt < max_retries:
                logger.warning("MedGemma attempt %d failed: %s — retrying", attempt + 1, exc)
                continue
            logger.error("MedGemma failed after %d attempts: %s", max_retries + 1, exc)
            raise

    raise RuntimeError("MedGemma: unexpected execution path")
