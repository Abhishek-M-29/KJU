"""
Pydantic models for the final diagnostic report — the pipeline's output.
Schema matches the JSON specification in AI/ai.md exactly.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ShapFeature(BaseModel):
    """A single SHAP feature contribution."""

    name: str = Field(..., description="Feature label, e.g. 'Ejection Fraction (35%)'")
    impact: float = Field(..., description="Magnitude of impact (positive = protective, negative = risk)")
    direction: str = Field(..., pattern="^(positive|negative)$")


class HeatmapEntry(BaseModel):
    """A single feature-category heatmap value."""

    name: str = Field(..., description="Category label, e.g. 'Cardiac Function'")
    value: float = Field(..., ge=0.0, le=1.0, description="Intensity 0.0–1.0")


class QualitativeFactors(BaseModel):
    """Structured qualitative findings from MedGemma + Synthesis."""

    riskFactors: list[str] = []
    protectiveFactors: list[str] = []
    recommendations: list[str] = []


class DiagnosticReport(BaseModel):
    """The complete diagnostic report produced by the pipeline."""

    jobId: str
    patientId: str
    generatedAt: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z"
    )
    status: str = "draft"
    executiveSummary: str = ""
    riskScore: int = Field(0, ge=0, le=100)
    shapFeatures: list[ShapFeature] = []
    featureHeatmap: list[HeatmapEntry] = []
    qualitativeFactors: QualitativeFactors = Field(default_factory=QualitativeFactors)
