# WTQ Utility Bill Decoder

AI-powered assistant that extracts details from Pakistani electricity bills (K-Electric, LESCO, IESCO) and answers customer questions in plain English.

Built for **Women Tech Quest Build Track 2026**.

---

## What It Does

- **Level 1 (Extraction):** Reads a bill image and extracts billing details as JSON.
- **Level 2 (Explanation):** Answers customer questions about the bill in plain English.

---

## Requirements

- **Python:** 3.11 or later (tested on 3.12.8)
- **API Key:** Google AI Studio (Gemini)

---

## Setup

### 1. Navigate to project folder

```
cd path/to/wtq-utility-bill-decoder
```

### 2. Create and activate virtual environment

```
python -m venv venv
source venv/Scripts/activate     # Windows (Git Bash)
source venv/bin/activate         # macOS / Linux
```

### 3. Install dependencies

```
pip install -r source/requirements.txt
```

### 4. Configure API key

```
cd source
cp .env.example .env
```

Edit `.env` and set your actual API key from Google AI Studio:

```
MODEL_PROVIDER=google
MODEL_NAME=gemini-3.5-flash-lite
API_KEY=your-actual-api-key-here
DATA_DIR=../data
OUTPUT_DIR=../output
```

**Never commit `.env` to version control.**

---

## Usage

### Option A: Command-Line (Batch Processing)

```
cd source
python src/main.py --mode level1      # Level 1 only
python src/main.py --mode level2      # Level 2 only
python src/main.py --mode all         # Both
python src/main.py --mode test-single --bill ../data/train/bills/KESC_0008.png
```

Outputs:
- `output/level1.csv` — one JSON per bill
- `output/level2.csv` — one answer per question

### Option B: Streamlit UI (Interactive)

```
cd source
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## Project Structure

```
wtq-utility-bill-decoder/
├── data/
│   ├── train/bills/
│   └── test/
│       ├── bills/
│       └── csv/
├── source/
│   ├── src/
│   │   ├── config.py
│   │   ├── llm_client.py
│   │   ├── extractor.py
│   │   ├── level1.py
│   │   ├── level2.py
│   │   └── main.py
│   ├── app.py
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── output/
│   ├── level1.csv
│   └── level2.csv
└── demo/
    └── demo.mp4
```

---

## AI Usage

### Models Used
- **Gemini 3.5 Flash-Lite** (`gemini-3.5-flash-lite`) via Google AI Studio

### APIs and Services
- **Google Generative AI SDK** (`google-genai==1.16.1`)
- **Google AI Studio** — API key management
- No prohibited services (no Azure, no Textract, no Mindee)

### Coding Assistants Used
- **Claude (Anthropic)** — helped draft and review code
- **Gemini** — used to test the API and debug

### Libraries
- `google-genai` — LLM API client
- `python-dotenv` — environment variable loading
- `Pillow` — image handling
- `tenacity` — retry logic for API failures
- `streamlit` — interactive UI
- `pytest` — testing

---

## Rules Compliance

- Only allowed LLMs used
- No prohibited services
- No personal identifiers extracted
- Numbers as numbers, dates in ISO format
- Null for unreadable values
- Credits and subsidies as negative numbers
- API key stored in `.env`, never committed

---

## License

Built for Women Tech Quest Build Track 2026. Educational use only.