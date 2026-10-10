"""Level 1 CSV generation."""
import csv
import json
import logging
from pathlib import Path

from config import TEST_BILLS_DIR, TEST_CSV_DIR, OUTPUT_DIR, ensure_output_dir
from extractor import BillExtractor

logger = logging.getLogger(__name__)


def process_level1(output_csv: Path = None) -> Path:
    """Process all test bills and write level1.csv."""
    ensure_output_dir()
    output_csv = output_csv or (OUTPUT_DIR / "level1.csv")

    template_path = TEST_CSV_DIR / "level1.csv"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    extractor = BillExtractor()

    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bill_id", "json"])

        for row in rows:
            bill_id = row["bill_id"]
            image_path = TEST_BILLS_DIR / f"{bill_id}.png"
            if not image_path.exists():
                image_path = TEST_BILLS_DIR / f"{bill_id}.jpg"

            if not image_path.exists():
                logger.error(f"Image not found for {bill_id}")
                writer.writerow([bill_id, "{}"])
                continue

            try:
                result = extractor.extract(image_path)
                json_str = json.dumps(result, ensure_ascii=False)
                writer.writerow([bill_id, json_str])
                logger.info(f"✅ {bill_id}")
            except Exception as e:
                logger.error(f"❌ {bill_id}: {e}")
                writer.writerow([bill_id, "{}"])

    return output_csv