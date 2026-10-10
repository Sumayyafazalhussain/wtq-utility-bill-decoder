"""Level 1 bill extraction using Gemini."""
import json
import logging
from pathlib import Path

from llm_client import LLMClient

logger = logging.getLogger(__name__)


LEVEL1_PROMPT = """You are extracting data from a Pakistani electricity bill.

Return ONLY a valid JSON object with EXACTLY these fields:
{
  "provider": "KE" or "LESCO" or "IESCO",
  "tariff": "string or null",
  "sanctioned_load_kw": number or null,
  "bill_month": "YYYY-MM or null",
  "reading_date": "YYYY-MM-DD or null",
  "issue_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "previous_reading": number or null,
  "current_reading": number or null,
  "units_consumed": number or null,
  "charges": [{"type": "...", "amount": number}, ...],
  "total_charges": number or null,
  "taxes": [{"type": "...", "amount": number}, ...],
  "total_taxes": number or null,
  "current_bill": number or null,
  "arrears": number or null,
  "payable_within_due_date": number or null,
  "payable_after_due_date": number or null
}

Charge types (use exactly): energy, fixed, fpa, quarterly_adjustment, surcharge, meter_rent, subsidy, other
Tax types (use exactly): gst, electricity_duty, income_tax, municipal_tax, other_tax

CRITICAL rules:
- Numbers must be numbers, not strings. Remove commas.
- Subsidies/credits are NEGATIVE (e.g., 38209CR becomes -38209)
- Dates must be YYYY-MM-DD format
- bill_month must be YYYY-MM format
- Skip blank or zero charge lines
- If a value is not visible, use null (do NOT guess)
- Do NOT include names, addresses, CNIC, account numbers
- For payable_after_due_date: if MULTIPLE late-payment amounts are shown,
  return the HIGHEST one (after the latest date)
- Return ONLY the JSON, no other text

Now extract from this bill image."""


class BillExtractor:
    """Extract Level 1 JSON from a bill image."""

    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()

    def extract(self, image_path: Path) -> dict:
        """Extract bill details from image."""
        logger.info(f"Extracting: {image_path.name}")

        result = self.client.generate_json(LEVEL1_PROMPT, image_path)

        required = [
            "provider", "tariff", "sanctioned_load_kw", "bill_month",
            "reading_date", "issue_date", "due_date",
            "previous_reading", "current_reading", "units_consumed",
            "charges", "total_charges", "taxes", "total_taxes",
            "current_bill", "arrears",
            "payable_within_due_date", "payable_after_due_date",
        ]
        for field in required:
            if field not in result:
                result[field] = [] if field in ("charges", "taxes") else None

        # Ensure provider matches filename
        filename = image_path.stem.upper()
        if filename.startswith("KESC"):
            result["provider"] = "KE"
        elif filename.startswith("LESCO"):
            result["provider"] = "LESCO"
        elif filename.startswith("IESCO"):
            result["provider"] = "IESCO"

        return result