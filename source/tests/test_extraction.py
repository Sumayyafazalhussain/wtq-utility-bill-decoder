"""Test bill extraction with tolerance for LLM variations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import TRAIN_BILLS_DIR
from extractor import BillExtractor


def test_kesc_0008():
    """Test KESC_0008 matches the worked example from the guide."""
    bill = TRAIN_BILLS_DIR / "KESC_0008.png"
    if not bill.exists():
        print(f"SKIP: {bill} not found")
        return

    extractor = BillExtractor()
    result = extractor.extract(bill)

    print(f"Provider: {result.get('provider')}")
    print(f"Units: {result.get('units_consumed')}")
    print(f"Bill: {result.get('current_bill')}")

    assert result["provider"] == "KE"
    assert result["units_consumed"] == 151

    def close(actual, expected, pct=0.05):
        if actual is None:
            return False
        return abs(actual - expected) / max(abs(expected), 1) < pct

    assert close(result["current_bill"], 3430.24)
    print("\n✅ KESC_0008 test PASSED")


if __name__ == "__main__":
    test_kesc_0008()