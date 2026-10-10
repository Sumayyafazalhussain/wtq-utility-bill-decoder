"""Configuration loader for WTQ Utility Bill Decoder."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from source/ folder
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)

# Project paths
SOURCE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SOURCE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

TRAIN_BILLS_DIR = DATA_DIR / "train" / "bills"
TEST_BILLS_DIR = DATA_DIR / "test" / "bills"
TEST_CSV_DIR = DATA_DIR / "test" / "csv"

# Model config
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "google")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.5-flash-lite")
API_KEY = os.getenv("API_KEY")

# Validation
if not API_KEY:
    raise ValueError("API_KEY not set in .env file")


def ensure_output_dir():
    """Create output directory if it does not exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR