# tools.py
import time
import random
from typing import Dict, Any
from utils import logger, safe_str, scrub_output_for_pii
from config import ENABLE_EXTERNAL_ENRICHMENT, ENRICHMENT_API_KEY
from google.adk.models.google_llm import Gemini
from google.genai import types
from observability import measure_time

# retry helper (simple)
def retry(fn, attempts=3, delay=1, backoff=2):
    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            wait = delay * (backoff ** i)
            logger.warning(f"Tool call failed (attempt {i+1}/{attempts}), retrying in {wait}s: {e}")
            time.sleep(wait)
    raise last_exc

# --- Research tool: deterministic mock + optional enrichment adapter
@measure_time("research_company")
def research_company(company_name: str) -> Dict[str, Any]:
    company_name = safe_str(company_name).strip()
    logger.info(f"[tool] research_company called for '{company_name}'")

    # deterministic mock baseline (safe for testing / evaluation)
    baseline = {
        "company_name": company_name,
        "industry": "Technology / SaaS",
        "stage": random.choice(["Seed", "Series A", "Series B", "Public"]),
        "employee_count_est": random.choice([25, 120, 500, 2000, 10000]),
        "summary": f"{company_name} is a company operating in the Technology vertical (deterministic mock)."
    }

    # Optional enrichment adapter: call a real enrichment API if enabled (you must provide key)
    if ENABLE_EXTERNAL_ENRICHMENT and ENRICHMENT_API_KEY:
        def call_enrichment():
            # placeholder - user implements actual integration
            logger.info("Calling external enrichment API (adapter)")
            # return enriched data dict
            return {
                "industry": "SaaS",
                "funding": "Series C",
                "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
                "summary": f"{company_name} appears to be a SaaS company (from enrichment)."
            }
        try:
            enriched = retry(call_enrichment, attempts=2, delay=1)
            baseline.update(enriched)
        except Exception as e:
            logger.warning(f"Enrichment adapter failed: {e}")

    # Scrub sensitive tokens before returning (safety)
    baseline["summary"] = scrub_output_for_pii(baseline["summary"])
    return baseline

# --- Lead scoring tool
@measure_time("score_lead")
def score_lead(company_name: str, employee_count: int, intent_score: int) -> Dict[str, Any]:
    logger.info(f"[tool] score_lead: {company_name}, employees={employee_count}, intent={intent_score}")
    # Strongly typed defensive checks
    try:
        employee_count = int(employee_count)
        intent_score = int(intent_score)
    except Exception:
        raise ValueError("employee_count and intent_score must be integers")

    # Scoring logic: configurable; deterministic for testing
    base = (employee_count / 100.0) + (intent_score * 3)
    score = round(base, 2)
    tier = "A" if score >= 12 else ("B" if score >= 6 else "C")
    return {"company_name": company_name, "score": score, "tier": tier}

# --- Outreach generation tool (uses Gemini model for naturalness but constraints responses)
@measure_time("generate_outreach")
def generate_outreach(company_name: str, contact_name: str, tier: str, model_client: Gemini=None) -> Dict[str, Any]:
    logger.info(f"[tool] generate_outreach: {company_name}, contact={contact_name}, tier={tier}")
    # Minimal templated approach to avoid hallucination: template + optional polish from LLM
    template = (
        f"Hi {contact_name},\n\n"
        f"I noticed {company_name} is growing rapidly. We help teams like yours accelerate sales operations by automating lead qualification and outreach.\n\n"
        "If you're open to a 15-minute sync, I'd love to share how companies reduced SDR time by 30%.\n\n"
        "Best,\nSales-ops team"
    )

    # If model_client provided, ask it to polish but with strict guardrails (no new facts)
    if model_client:
        def call_model():
            # WARNING: model polish must be instructed not to add facts
            prompt = (
                "Polish the following outreach email for tone and clarity. "
                "DO NOT add any company-specific factual claims (no funding, no tech stack). "
                f"Email:\n\n{template}"
            )
            # Using the genai library client wrapper for demonstration – adapt to API used
            # NOTE: the ADK Gemini wrapper usage must match your installed version; this is illustrative
            response = model_client.generate(prompt=prompt, max_output_tokens=200)
            # depending on client lib, extract text
            polished = response.text if hasattr(response, "text") else str(response)
            return polished
        try:
            polished = retry(call_model, attempts=2, delay=0.5)
            polished = scrub_output_for_pii(polished)
            return {"email": polished, "tier": tier}
        except Exception as e:
            logger.warning(f"Model polish failed: {e}")

    return {"email": template, "tier": tier}
