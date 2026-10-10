"""WTQ Utility Bill Decoder - Professional Streamlit UI"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import TRAIN_BILLS_DIR, MODEL_NAME
from extractor import BillExtractor
from level2 import QuestionAnswerer

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="WTQ Bill Decoder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ CUSTOM CSS ============
st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(rgba(10, 15, 40, 0.88), rgba(10, 15, 40, 0.92)),
            url("https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1300px;
    }
    .hero-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(147, 51, 234, 0.95) 100%);
        border-radius: 18px;
        padding: 36px 28px;
        text-align: center;
        margin-bottom: 26px;
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
    }
    .hero-header h1 {
        color: #ffffff !important;
        font-size: 2.4rem;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .hero-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.05rem;
        margin-top: 10px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 22px 18px;
        color: white;
        text-align: center;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        border-color: rgba(96, 165, 250, 0.6);
    }
    .metric-card .icon { font-size: 1.6rem; margin-bottom: 8px; }
    .metric-label {
        font-size: 0.75rem; text-transform: uppercase;
        letter-spacing: 1.5px; opacity: 0.75;
        margin-bottom: 6px; color: #93c5fd;
    }
    .metric-value {
        font-size: 1.5rem; font-weight: 700;
        color: #ffffff; word-break: break-word;
    }
    .answer-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(59, 130, 246, 0.12) 100%);
        border-left: 4px solid #10b981;
        padding: 20px 24px;
        border-radius: 12px;
        margin: 16px 0;
        font-size: 1.02rem;
        line-height: 1.7;
        color: #f1f5f9;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
        backdrop-filter: blur(8px);
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 18px rgba(59, 130, 246, 0.35);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5);
        filter: brightness(1.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.7) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #60a5fa !important; }
    [data-testid="stSidebar"] code {
        background: rgba(59, 130, 246, 0.15);
        color: #93c5fd !important;
        padding: 4px 8px;
        border-radius: 6px;
    }
    h1, h2, h3, h4, h5 { color: #ffffff !important; }
    p, label, .stMarkdown { color: rgba(255, 255, 255, 0.9); }
    .stAlert { border-radius: 12px; backdrop-filter: blur(8px); }
    [data-testid="stFileUploader"] section {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(96, 165, 250, 0.4);
        border-radius: 12px;
    }
    .footer-note {
        text-align: center;
        color: rgba(255, 255, 255, 0.5);
        padding: 24px 0 8px 0;
        font-size: 0.85rem;
    }
    .footer-note span { color: #60a5fa; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============ HERO ============
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-badge">⚡ WOMEN TECH QUEST 2026</div>
        <h1>WTQ Utility Bill Decoder</h1>
        <p>AI-powered extraction & explanation for K-Electric, LESCO, and IESCO bills</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.markdown("---")
    st.markdown("### 🤖 Active Model")
    st.code(MODEL_NAME, language="text")
    st.markdown("### ✅ Allowed Models")
    st.markdown("- Gemini 3.5 Flash-Lite\n- Gemini 3.1 Flash-Lite")
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    st.markdown(
        "1. **Upload** a bill image\n"
        "2. **Click** Extract Bill Details\n"
        "3. **Ask** questions in Q&A tab\n"
        "4. **Download** JSON if needed"
    )
    st.markdown("---")
    st.markdown("### 📊 Live Stats")
    if st.session_state.get("extracted"):
        r = st.session_state.extracted
        st.markdown(f"- Provider: **{r.get('provider', 'N/A')}**")
        st.markdown(f"- Units: **{r.get('units_consumed', 'N/A')}**")
        st.markdown(f"- Bill: **Rs. {r.get('current_bill', 'N/A')}**")
    else:
        st.markdown("_No bill extracted yet_")

# ============ SESSION STATE ============
if "extracted" not in st.session_state:
    st.session_state.extracted = None
if "bill_name" not in st.session_state:
    st.session_state.bill_name = None
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# ============ TABS ============
tab1, tab2, tab3, tab4 = st.tabs(
    ["📄 Extract Bill", "💬 Ask Questions", "📜 History", "ℹ️ About"]
)

# ============ TAB 1 ============
with tab1:
    st.markdown("### 📄 Level 1 — Bill Extraction")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 📤 Upload Your Bill")
        uploaded_file = st.file_uploader(
            "Choose a bill image",
            type=["png", "jpg", "jpeg"],
            key="bill_uploader",
            label_visibility="collapsed",
        )
        st.markdown("#### 🎯 Or Pick a Sample")
        sample_bills = (
            sorted(TRAIN_BILLS_DIR.glob("*")) if TRAIN_BILLS_DIR.exists() else []
        )
        sample_names = ["-- Select a sample --"] + [b.name for b in sample_bills]
        selected_sample = st.selectbox(
            "Sample bills", sample_names, label_visibility="collapsed"
        )

    with col2:
        st.markdown("#### 🖼️ Bill Preview")
        preview_shown = False
        if uploaded_file:
            st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
            preview_shown = True
        elif selected_sample and selected_sample != "-- Select a sample --":
            sample_path = TRAIN_BILLS_DIR / selected_sample
            if sample_path.exists():
                st.image(str(sample_path), caption=selected_sample, use_container_width=True)
                preview_shown = True
        if not preview_shown:
            st.info("👈 Upload a bill or select a sample to preview")

    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        extract_clicked = st.button(
            "🚀 Extract Bill Details", type="primary", use_container_width=True
        )

    if extract_clicked:
        image_path = None
        bill_name = None

        if uploaded_file:
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded_file.name).suffix
            )
            tmp.write(uploaded_file.getbuffer())
            tmp.close()
            image_path = Path(tmp.name)
            bill_name = uploaded_file.name
        elif selected_sample and selected_sample != "-- Select a sample --":
            image_path = TRAIN_BILLS_DIR / selected_sample
            bill_name = selected_sample
        else:
            st.error("⚠️ Please upload a bill or select a sample first.")
            st.stop()

        if image_path and image_path.exists():
            with st.spinner(f"🤖 AI is reading your bill... Please wait"):
                try:
                    extractor = BillExtractor()
                    result = extractor.extract(image_path)
                    st.session_state.extracted = result
                    st.session_state.bill_name = bill_name
                    st.success(f"✅ Extracted successfully from **{bill_name}**")
                except Exception as e:
                    st.error(f"❌ Extraction failed: {e}")

    if st.session_state.extracted:
        result = st.session_state.extracted
        st.markdown("---")
        st.markdown("### 📊 Extracted Data")

        provider = result.get("provider") or "N/A"
        units = result.get("units_consumed") or "N/A"
        bill_amt = result.get("current_bill")
        due = result.get("due_date") or "N/A"

        c1, c2, c3, c4 = st.columns(4, gap="small")

        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="icon">🏢</div>
                    <div class="metric-label">Provider</div>
                    <div class="metric-value">{provider}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="icon">⚡</div>
                    <div class="metric-label">Units Consumed</div>
                    <div class="metric-value">{units}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            bill_display = (
                f"{bill_amt:,.2f}" if isinstance(bill_amt, (int, float)) else "N/A"
            )
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="icon">💰</div>
                    <div class="metric-label">Current Bill</div>
                    <div class="metric-value">Rs. {bill_display}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="icon">📅</div>
                    <div class="metric-label">Due Date</div>
                    <div class="metric-value" style="font-size:1.15rem;">{due}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("")
        sub1, sub2, sub3 = st.tabs(["📋 Full JSON", "💰 Charges", "🧾 Taxes"])

        with sub1:
            st.json(result)
        with sub2:
            charges = result.get("charges", [])
            if charges:
                st.dataframe(charges, use_container_width=True)
                st.markdown(f"**Total Charges:** Rs. {result.get('total_charges', 'N/A')}")
            else:
                st.info("No charges extracted")
        with sub3:
            taxes = result.get("taxes", [])
            if taxes:
                st.dataframe(taxes, use_container_width=True)
                st.markdown(f"**Total Taxes:** Rs. {result.get('total_taxes', 'N/A')}")
            else:
                st.info("No taxes extracted")

        st.markdown("---")
        st.download_button(
            "📥 Download Extracted JSON",
            data=json.dumps(result, indent=2),
            file_name=f"{st.session_state.bill_name}.json",
            mime="application/json",
        )

# ============ TAB 2 ============
with tab2:
    st.markdown("### 💬 Level 2 — Ask Questions")

    if not st.session_state.extracted:
        st.warning("⚠️ Please extract a bill first in the **Extract Bill** tab.")
    else:
        st.info(f"📄 Bill loaded: **{st.session_state.bill_name}**")
        st.markdown("#### 🚀 Quick Questions")
        qcols = st.columns(2, gap="small")
        quick_qs = [
            "How much is my current bill?",
            "How many units did I consume?",
            "How much are the taxes?",
            "What is my due date?",
            "What is the breakdown of charges?",
            "How much is the fuel price adjustment?",
        ]

        selected_quick = None
        for i, q in enumerate(quick_qs):
            with qcols[i % 2]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    selected_quick = q

        st.markdown("#### ✍️ Or Ask Your Own Question")
        custom_q = st.text_input(
            "Your question",
            key="custom_q",
            placeholder="e.g., What percentage of my bill is taxes?",
        )

        question = selected_quick or custom_q

        if st.button("💬 Get Answer", type="primary", use_container_width=True):
            if not question:
                st.error("Please type or select a question.")
            else:
                with st.spinner("🤔 Thinking..."):
                    try:
                        qa = QuestionAnswerer()
                        answer = qa.answer(st.session_state.extracted, question)
                        st.markdown("### 💡 Answer")
                        st.markdown(
                            f'<div class="answer-box">{answer}</div>',
                            unsafe_allow_html=True,
                        )
                        st.session_state.qa_history.append(
                            {
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "bill": st.session_state.bill_name,
                                "question": question,
                                "answer": answer,
                            }
                        )
                    except Exception as e:
                        st.error(f"❌ Failed: {e}")

# ============ TAB 3 ============
with tab3:
    st.markdown("### 📜 Question History")
    if not st.session_state.qa_history:
        st.info("No questions asked yet. Go to the **Ask Questions** tab to start.")
    else:
        for i, item in enumerate(reversed(st.session_state.qa_history), 1):
            with st.expander(f"Q{i}: {item['question']}  —  {item['time']}"):
                st.markdown(f"**Bill:** {item['bill']}")
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Answer:** {item['answer']}")
        if st.button("🗑️ Clear History"):
            st.session_state.qa_history = []
            st.rerun()

# ============ TAB 4 ============
with tab4:
    st.markdown("### ℹ️ About This Project")
    st.markdown(
        """
        #### 🎯 WTQ Utility Bill Decoder

        Built for **Women Tech Quest Build Track 2026**.

        #### What It Does

        - **Level 1 (Extraction):** Extracts billing details from Pakistani electricity bills.
        - **Level 2 (Explanation):** Answers customer questions in plain English.

        #### 🛠️ Technology Stack

        | Component | Technology |
        |---|---|
        | AI Model | Gemini 3.5 Flash-Lite |
        | Language | Python 3.12 |
        | UI Framework | Streamlit |
        | SDK | google-genai 1.16.1 |

        #### ✅ Rules Compliance

        - Only allowed LLMs used
        - No prohibited services (Azure, Textract, Mindee)
        - No personal identifiers extracted
        - Numbers as numbers, dates in ISO format
        - Null for unreadable values
        """
    )

# ============ FOOTER ============
st.markdown(
    """
    <div class="footer-note">
        Made with ❤️ for <span>Women Tech Quest Build Track 2026</span>
    </div>
    """,
    unsafe_allow_html=True,
)