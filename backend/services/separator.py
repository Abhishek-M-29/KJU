"""
Medical Detail Extractor — LLM-powered filter for MedGemma.

Takes the raw patient context and uses a Groq LLM to extract only the
medically relevant details (symptoms, history, diagnoses, clinical notes,
lifestyle factors, medications, etc.), then appends a diagnosis prompt.

This filtered text is what gets sent to MedGemma for NER + qualitative analysis.
The ML Swarm receives the full raw context directly (it has its own filtering).
"""

from __future__ import annotations

import json
import logging

from groq import AsyncGroq

from core.config import settings

logger = logging.getLogger(__name__)

# ── System prompt for the Medical Detail Extractor ──

EXTRACTOR_SYSTEM_PROMPT = """\
You are a clinical data filter. Your job is to receive raw patient data \
(which may be structured JSON, free-form text, a mix of both, or messy notes) \
and extract ONLY the medically relevant details into clean, natural-language text.

Include:
- Symptoms and complaints (presenting, historical, subjective)
- Clinical summaries, doctor notes, radiology reports, discharge summaries
- Diagnoses, conditions, and medical history
- Vital signs and lab values in clinical context
- Medications, dosages, and treatment history
- Allergies and adverse reactions
- Family medical history
- Lifestyle factors (smoking, alcohol, diet, exercise, occupation)
- Surgical history
- Any other clinically significant information

Exclude:
- System metadata (job IDs, doctor IDs, timestamps unrelated to care)
- UI/formatting artifacts
- Duplicate information (mention each fact once)

Output ONLY a clean natural-language summary of the medical details. \
Write in clinical prose, not bullet points or JSON. \
Do NOT add any diagnosis or interpretation — just extract and present the facts.
"""


async def extract_medical_details(raw_data: str) -> str:
    """
    Use an LLM to filter medical details from raw patient data, then
    append a diagnosis prompt for MedGemma.

    Args:
        raw_data: The raw patient data — could be JSON string, free text,
                  or any mix.

    Returns:
        A clean medical summary string ending with
        "What preliminary diagnosis can be made from this"
    """
    client = AsyncGroq(api_key=settings.groq_api_key)

    logger.info("Extractor: calling Groq to filter medical details (%d chars)", len(raw_data))

    chat_completion = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": raw_data},
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    medical_text = chat_completion.choices[0].message.content or ""
    logger.info("Extractor: extracted %d chars of medical details", len(medical_text))

    # Append the diagnosis prompt for MedGemma
    medgemma_query = f"{medical_text}\n\nWhat preliminary diagnosis can be made from this"

    logger.info("Extractor: final MedGemma query: %.200s...", medgemma_query)
    return medgemma_query

