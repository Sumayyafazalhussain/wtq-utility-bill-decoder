"""Main entry point for WTQ Utility Bill Decoder."""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import TRAIN_BILLS_DIR, OUTPUT_DIR
from extractor import BillExtractor
from level1 import process_level1
from level2 import process_level2


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def test_single_bill(image_path: Path):
    """Test extraction on a single bill."""
    extractor = BillExtractor()
    result = extractor.extract(image_path)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="WTQ Utility Bill Decoder")
    parser.add_argument(
        "--mode",
        choices=["test-single", "level1", "level2", "all"],
        default="all",
        help="What to run",
    )
    parser.add_argument("--bill", type=str, help="Bill path for test-single mode")
    args = parser.parse_args()

    setup_logging()

    if args.mode == "test-single":
        bill = Path(args.bill) if args.bill else (TRAIN_BILLS_DIR / "KESC_0008.png")
        if not bill.exists():
            print(f"❌ Bill not found: {bill}")
            sys.exit(1)
        print(f"🔍 Testing: {bill.name}")
        test_single_bill(bill)
        return

    if args.mode in ("level1", "all"):
        print("🚀 Running Level 1...")
        result = process_level1()
        print(f"✅ Level 1 done: {result}")

    if args.mode in ("level2", "all"):
        print("🚀 Running Level 2...")
        result = process_level2()
        print(f"✅ Level 2 done: {result}")

    print("\n🎉 All done!")


if __name__ == "__main__":
    main()