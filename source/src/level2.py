"""Level 2 question answering."""
import csv
import json
import logging
from pathlib import Path

from config import TEST_CSV_DIR, OUTPUT_DIR, ensure_output_dir
from llm_client import LLMClient

logger = logging.getLogger(__name__)


LEVEL2_PROMPT = """You are answering a customer question about their electricity bill.

Bill data (JSON):
{bill_json}

Question: {question}

Rules:
- Answer in English only.
- Use ONLY the bill data above. Do NOT use outside tariff information.
- If information is not available, say so clearly.
- Show your calculations when the answer requires arithmetic.
- Label estimates as estimates.
- Keep the answer short (1-3 sentences).
- Do not include personal identifiers.

Answer:"""


class QuestionAnswerer:
    """Answer Level 2 questions using bill JSON."""

    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()

    def answer(self, bill_json: dict, question: str) -> str:
        """Answer a single question."""
        bill_str = json.dumps(bill_json, ensure_ascii=False)
        prompt = LEVEL2_PROMPT.format(bill_json=bill_str, question=question)
        try:
            return self.client.generate(prompt).strip()
        except Exception as e:
            logger.error(f"Answer failed: {e}")
            return f"Unable to answer: {e}"


def process_level2(output_csv: Path = None) -> Path:
    """Process all test questions and write level2.csv."""
    ensure_output_dir()
    output_csv = output_csv or (OUTPUT_DIR / "level2.csv")

    level1_path = OUTPUT_DIR / "level1.csv"
    if not level1_path.exists():
        raise FileNotFoundError("level1.csv not found. Run level1 first.")

    bill_data = {}
    with open(level1_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                bill_data[row["bill_id"]] = json.loads(row["json"])
            except Exception:
                bill_data[row["bill_id"]] = {}

    template_path = TEST_CSV_DIR / "level2.csv"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    qa = QuestionAnswerer()

    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bill_id", "question_id", "question", "answer"])

        for row in rows:
            bill_id = row["bill_id"]
            qid = row["question_id"]
            question = row["question"]

            if bill_id not in bill_data:
                writer.writerow([bill_id, qid, question, "Bill data not available."])
                continue

            try:
                answer = qa.answer(bill_data[bill_id], question)
                writer.writerow([bill_id, qid, question, answer])
                logger.info(f"✅ {bill_id} {qid}")
            except Exception as e:
                logger.error(f"❌ {bill_id} {qid}: {e}")
                writer.writerow([bill_id, qid, question, f"Error: {e}"])

    return output_csv