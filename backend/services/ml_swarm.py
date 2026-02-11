"""
ML Swarm API client.

The ML Swarm is an ensemble of lightweight task-specific models (Gradient Boosting /
Random Forests) that runs on structured/numeric patient data and returns:
  - Risk probability scores
  - SHAP feature contributions
  - Feature heatmap values

Some fields in the response may be null — the caller must handle that.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

# Timeout: 30s connect, 60s read (model inference can be slow)
_TIMEOUT = httpx.Timeout(connect=30.0, read=60.0, write=30.0, pool=30.0)


class SwarmResponse:
    """Parsed ML Swarm result. All fields are optional since the API may return nulls."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.risk_score: Optional[int] = raw.get("riskScore")
        self.shap_features: Optional[list[dict]] = raw.get("shapFeatures")
        self.feature_heatmap: Optional[list[dict]] = raw.get("featureHeatmap")
        self.risk_probabilities: Optional[dict] = raw.get("riskProbabilities")
        self.model_outputs: Optional[dict] = raw.get("modelOutputs")

    def __repr__(self) -> str:
        return f"SwarmResponse(risk_score={self.risk_score}, features={len(self.shap_features or [])})"


async def analyze(query: str) -> SwarmResponse:
    """
    Send structured patient data (as natural-language query) to the ML Swarm.

    Args:
        query: Natural language summary of numeric patient data.
              e.g. "Patient age 71, Male, BP 165/105, HR 88, ..."

    Returns:
        SwarmResponse with risk scores, SHAP features, and heatmap data.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses after retry.
        httpx.TimeoutException: On timeout after retry.
    """
    payload = {
        "text": query,
        "api_key": settings.groq_api_key,
    }
    max_retries = 1

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                logger.info(
                    "ML Swarm request (attempt %d): %s", attempt + 1, settings.ml_swarm_url
                )
                response = await client.post(settings.ml_swarm_url, json=payload)
                response.raise_for_status()

                data = response.json()
                logger.info("ML Swarm response received: risk_score=%s", data.get("riskScore"))
                return SwarmResponse(data)

        except (httpx.HTTPStatusError, httpx.TimeoutException) as exc:
            if attempt < max_retries:
                logger.warning("ML Swarm attempt %d failed: %s — retrying", attempt + 1, exc)
                continue
            logger.error("ML Swarm failed after %d attempts: %s", max_retries + 1, exc)
            raise

    # Should never reach here, but satisfy type checker
    raise RuntimeError("ML Swarm: unexpected execution path")
