import streamlit as st
from google import genai
import re

st.set_page_config(
    page_title="ClearCommitment",
    page_icon="📋",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif;
    background-color: #0e1117;
    color: #e8e6e1;
}
.stApp { background: #0e1117; }
#MainMenu, footer, header { visibility: hidden; }
.cc-hero {
    position: relative;
    padding: 3.5rem 2.5rem 3rem;
    margin-bottom: 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #0f2942 0%, #0a1628 60%, #091020 100%);
    border: 1px solid rgba(99, 160, 255, 0.15);
    overflow: hidden;
    text-align: center;
}
.cc-hero::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%;
    transform: translateX(-50%);
    width: 400px; height: 200px;
    background: radial-gradient(ellipse, rgba(59, 130, 246, 0.18) 0%, transparent 70%);
    pointer-events: none;
}
.cc-hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,160,255,0.3), transparent);
}
.cc-wordmark {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    letter-spacing: -1px;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.cc-wordmark span { color: #60a5fa; }
.cc-tagline {
    font-size: 15px;
    color: rgba(232,230,225,0.55);
    font-weight: 300;
    letter-spacing: 0.02em;
    margin-bottom: 1.5rem;
}
.cc-badges {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}
.cc-badge {
    font-size: 11px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 100px;
    border: 1px solid rgba(99,160,255,0.25);
    color: rgba(232,230,225,0.6);
    background: rgba(99,160,255,0.06);
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.cc-disclaimer {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: rgba(234, 179, 8, 0.06);
    border: 1px solid rgba(234, 179, 8, 0.2);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 13px;
    color: rgba(234,179,8,0.8);
    margin-bottom: 1.8rem;
    line-height: 1.5;
}
.cc-card {
    background: #161b27;
    border: 1px solid rgba(99,160,255,0.1);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 0.4rem;
    font-size: 14.5px;
    line-height: 1.85;
    white-space: pre-wrap;
    color: #d4d0c8;
}
.cc-card-danger {
    background: #1a1008;
    border: 1px solid rgba(251, 146, 60, 0.25);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 0.4rem;
    font-size: 14.5px;
    line-height: 1.85;
    white-space: pre-wrap;
    color: #d4d0c8;
}
.cc-card-success {
    background: #0a1a0f;
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 0.4rem;
    font-size: 14.5px;
    line-height: 1.85;
    white-space: pre-wrap;
    color: #d4d0c8;
}
.cc-section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.8rem 0 0.3rem;
}
.cc-section-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}
.cc-section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 17px;
    color: #e8e6e1;
    letter-spacing: -0.3px;
}
.cc-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,160,255,0.15), transparent);
    margin: 2rem 0;
}
.cc-analysis-header {
    text-align: center;
    margin: 2rem 0 1.5rem;
}
.cc-analysis-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
}
.cc-analysis-sub {
    font-size: 13px;
    color: rgba(232,230,225,0.4);
}
.cc-footer {
    text-align: center;
    font-size: 12px;
    color: rgba(232,230,225,0.2);
    padding: 1.5rem 0 0.5rem;
    letter-spacing: 0.02em;
}
.stSelectbox > div > div {
    background: #161b27 !important;
    border: 1px solid rgba(99,160,255,0.15) !important;
    border-radius: 10px !important;
    color: #e8e6e1 !important;
}
.stTextArea textarea {
    background: #161b27 !important;
    border: 1px solid rgba(99,160,255,0.15) !important;
    border-radius: 10px !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,160,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(99,160,255,0.08) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    box-shadow: 0 6px 24px rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    background: rgba(99,160,255,0.08) !important;
    color: #60a5fa !important;
    border: 1px solid rgba(99,160,255,0.2) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}
label, .stSelectbox label, .stTextArea label, .stFileUploader label {
    color: rgba(232,230,225,0.5) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)


def scrub_pii(text: str) -> str:
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', text)
    text = re.sub(r'(\+?1?\s?)?(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})', '[PHONE REDACTED]', text)
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
    return text


def call_gemini(system: str, user_msg: str) -> str:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return "⚠️ No API key found. Add GEMINI_API_KEY to your Streamlit secrets."
    try:
        client = genai.Client(api_key=api_key)
        clean_msg = scrub_pii(user_msg)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system}\n\n{clean_msg}"
        )
        return scrub_pii(response.text)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


st.markdown("""
<div class="cc-hero">
    <div class="cc-wordmark">Clear<span>Commitment</span></div>
    <div class="cc-tagline">AI-powered title commitment review — plain English, instantly</div>
    <div class="cc-badges">
        <span class="cc-badge">🔒 PII Protected</span>
        <span class="cc-badge">⚡ Instant Analysis</span>
        <span class="cc-badge">🏠 Title Industry</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cc-disclaimer">
    ⚠️ ClearCommitment is for informational purposes only. Always consult a licensed title attorney before closing.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Report type", [
        "Buyer — plain English, no jargon",
        "Real estate agent — risks and action items",
        "Attorney — detailed technical summary",
    ])
with col2:
    state = st.selectbox("State", ["Not specified"] + [
        "Alabama","Alaska","Arizona","Arkansas","California","Colorado",
        "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho",
        "Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
        "Maryland","Massachusetts","Michigan","Minnesota","Mississippi",
        "Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
        "New Mexico","New York","North Carolina","North Dakota","Ohio",
        "Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina",
        "South Dakota","Tennessee","Texas","Utah","Vermont","Virginia",
        "Washington","West Virginia","Wisconsin","Wyoming"
    ])

uploaded = st.file_uploader("Upload title commitment (.txt)", type=["txt"])
raw_text = ""
if uploaded:
    raw_text = uploaded.read().decode("utf-8", errors="ignore")
    st.success(f"✅ Loaded: {uploaded.name} ({len(raw_text):,} characters)")

commitment_text = st.text_area(
    "Paste title commitment text",
    value=raw_text,
    placeholder="Paste the full text of the title commitment here...",
    height=220,
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
analyze = st.button("Analyze Commitment →", type="primary", use_container_width=True)

if analyze:
    if not commitment_text.strip():
        st.warning("Please paste or upload a title commitment first.")
    else:
        state_note = f" Apply {state} state law and customs where relevant." if state != "Not specified" else ""

        with st.spinner("Analyzing your title commitment..."):

            system_summary = f"""You are an expert title insurance attorney explaining a title commitment to a {audience}.
Use plain English.{state_note}
Structure your response as:

PROPERTY SUMMARY:
(Property address, legal description in simple terms, type of title insurance)

WHAT THIS MEANS FOR THE BUYER:
(2-3 sentences explaining what a title commitment is)

SCHEDULE A — THE BASICS:
(Effective date, proposed insured, amount of insurance, type of estate)

SCHEDULE B-I — REQUIREMENTS:
(List each requirement in plain English)

SCHEDULE B-II — EXCEPTIONS:
(List each exception in plain English)"""

            summary = call_gemini(system_summary, f"Title commitment:\n\n{commitment_text[:5000]}")

            system_flags = f"""You are an expert title attorney.{state_note} Identify RED FLAGS in this title commitment.

Format as:
RED FLAGS:
- (Each red flag — specific, what it means, why it matters)

If none: write exactly "No significant red flags identified." """

            flags = call_gemini(system_flags, f"Review for red flags:\n\n{commitment_text[:5000]}")

            system_actions = f"""You are an expert title attorney.{state_note} List action items before closing.

Format as:
ACTION ITEMS:
- (Specific, actionable items only)"""

            actions = call_gemini(system_actions, f"List action items:\n\n{commitment_text[:5000]}")

        st.markdown('<div class="cc-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="cc-analysis-header">
            <div class="cc-analysis-title">Commitment Analysis</div>
            <div class="cc-analysis-sub">Review all findings carefully with your attorney</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cc-section-header">
            <div class="cc-section-icon" style="background:rgba(99,160,255,0.1)">📄</div>
            <div class="cc-section-title">Plain English Summary</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="cc-card">{summary}</div>', unsafe_allow_html=True)

        no_flags = "No significant" in flags
        flag_icon = "✅" if no_flags else "⚠️"
        flag_bg = "rgba(34,197,94,0.08)" if no_flags else "rgba(251,146,60,0.08)"
        st.markdown(f"""
        <div class="cc-section-header">
            <div class="cc-section-icon" style="background:{flag_bg}">{flag_icon}</div>
            <div class="cc-section-title">Red Flags</div>
        </div>
        """, unsafe_allow_html=True)
        card_class = "cc-card-success" if no_flags else "cc-card-danger"
        st.markdown(f'<div class="{card_class}">{flags}</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="cc-section-header">
            <div class="cc-section-icon" style="background:rgba(99,160,255,0.1)">✅</div>
            <div class="cc-section-title">Action Items Before Closing</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="cc-card">{actions}</div>', unsafe_allow_html=True)

        st.markdown('<div class="cc-divider"></div>', unsafe_allow_html=True)

        full_report = (
            f"CLEARCOMMITMENT ANALYSIS REPORT\n"
            f"{'='*50}\n"
            f"Report Type: {audience}\n"
            f"State: {state}\n"
            f"{'='*50}\n\n"
            f"PLAIN ENGLISH SUMMARY\n{'-'*30}\n{summary}\n\n"
            f"RED FLAGS\n{'-'*30}\n{flags}\n\n"
            f"ACTION ITEMS\n{'-'*30}\n{actions}\n\n"
            f"{'='*50}\n"
            f"Generated by ClearCommitment · For informational purposes only\n"
            f"Not a substitute for licensed title attorney review."
        )

        st.download_button(
            "📥 Download Full Report",
            data=full_report,
            file_name="ClearCommitment_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

st.markdown('<div class="cc-footer">ClearCommitment · AI-assisted title review · Not a law firm · Always verify with a licensed title attorney</div>', unsafe_allow_html=True)