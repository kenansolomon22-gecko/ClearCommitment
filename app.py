import streamlit as st
import google.generativeai as genai
import re

st.set_page_config(
    page_title="ClearCommitment",
    page_icon="📋",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.hero {
    background: linear-gradient(135deg, #1a3c5e 0%, #2563a8 100%);
    border-radius: 14px;
    padding: 2.2rem 2rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    color: white;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 6px;
    letter-spacing: -0.5px;
}
.hero p {
    font-size: 15px;
    opacity: 0.85;
    margin: 0;
}
.hero .tagline {
    font-size: 13px;
    opacity: 0.65;
    margin-top: 6px;
    font-style: italic;
}
.disclaimer {
    background: #f0f4ff;
    border-left: 3px solid #2563a8;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
    color: #444;
    margin-bottom: 1.2rem;
}
.result-box {
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-top: 0.5rem;
    font-size: 15px;
    line-height: 1.8;
    white-space: pre-wrap;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.flag-box {
    background: #fff8f0;
    border: 1px solid #fd7e14;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-top: 0.5rem;
    font-size: 15px;
    line-height: 1.8;
    white-space: pre-wrap;
    box-shadow: 0 1px 4px rgba(253,126,20,0.08);
}
.good-box {
    background: #f0fff4;
    border: 1px solid #198754;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-top: 0.5rem;
    font-size: 15px;
    line-height: 1.8;
    white-space: pre-wrap;
    box-shadow: 0 1px 4px rgba(25,135,84,0.08);
}
.section-label {
    font-size: 11px;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 5px;
    margin-top: 1.2rem;
}
.powered {
    text-align: center;
    font-size: 11px;
    color: #adb5bd;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── PII Scrubber ──────────────────────────────────────────────────────────────
def scrub_pii(text: str) -> str:
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', text)
    text = re.sub(r'(\+?1?\s?)?(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})', '[PHONE REDACTED]', text)
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
    return text


# ── Gemini API call ───────────────────────────────────────────────────────────
def call_gemini(system: str, user_msg: str) -> str:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return "⚠️ No API key found. Add GEMINI_API_KEY to your Streamlit secrets."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system
        )
        clean_msg = scrub_pii(user_msg)
        response = model.generate_content(clean_msg)
        return scrub_pii(response.text)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📋 ClearCommitment</h1>
    <p>Instant plain-English title commitment review</p>
    <div class="tagline">Powered by AI · Built for real estate professionals</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="disclaimer">⚠️ ClearCommitment is for informational purposes only. '
    'Always consult a licensed title attorney before closing.</div>',
    unsafe_allow_html=True
)

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("📌 Report type", [
        "Buyer — plain English, no jargon",
        "Real estate agent — risks and action items",
        "Attorney — detailed technical summary",
    ])
with col2:
    state = st.selectbox("📍 State", ["Not specified"] + [
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

uploaded = st.file_uploader("📁 Upload title commitment (.txt)", type=["txt"])
raw_text = ""
if uploaded:
    raw_text = uploaded.read().decode("utf-8", errors="ignore")
    st.success(f"✅ Loaded: {uploaded.name} ({len(raw_text):,} characters)")

commitment_text = st.text_area(
    "📝 Or paste title commitment text here",
    value=raw_text,
    placeholder="Paste the full text of the title commitment here...",
    height=200,
)

# ── Analyze ───────────────────────────────────────────────────────────────────
if st.button("🔍 Analyze Commitment", type="primary", use_container_width=True):
    if not commitment_text.strip():
        st.warning("Please paste or upload a title commitment first.")
    else:
        state_note = f" Apply {state} state law and customs where relevant." if state != "Not specified" else ""

        with st.spinner("Analyzing your title commitment..."):

            system_summary = f"""You are an expert title insurance attorney explaining a title commitment to a {audience}.
Use plain English — no legal jargon unless necessary, and explain any terms you use.{state_note}
Structure your response as:

PROPERTY SUMMARY:
(Property address, legal description in simple terms, type of title insurance)

WHAT THIS MEANS FOR THE BUYER:
(2-3 sentences explaining what a title commitment is and what it guarantees in simple terms)

SCHEDULE A — THE BASICS:
(Effective date, proposed insured, amount of insurance, type of estate)

SCHEDULE B-I — REQUIREMENTS:
(List each requirement in plain English — what needs to happen before closing)

SCHEDULE B-II — EXCEPTIONS:
(List each exception in plain English — what the title insurance will NOT cover)

Keep it clear, friendly, and actionable."""

            summary = call_gemini(system_summary, f"Title commitment:\n\n{commitment_text[:5000]}")

            system_flags = f"""You are an expert title attorney.{state_note} Review this title commitment and identify RED FLAGS or unusual items a buyer should be concerned about.

Format as:
RED FLAGS:
- (Each red flag — be specific about what it means and why it matters)

If none, write exactly: "No significant red flags identified."

Focus on things affecting the buyer's use, ownership, or resale of the property."""

            flags = call_gemini(system_flags, f"Review for red flags:\n\n{commitment_text[:5000]}")

            system_actions = f"""You are an expert title attorney.{state_note} List specific action items the buyer or attorney should take before closing based on this title commitment.

Format as:
ACTION ITEMS:
- (Each action item — be specific)

Focus on: items to clear, documents needed, questions to ask, things to verify."""

            actions = call_gemini(system_actions, f"List action items:\n\n{commitment_text[:5000]}")

        # ── Results ───────────────────────────────────────────────────────────
        st.divider()
        st.subheader("📋 ClearCommitment Analysis")

        st.markdown('<div class="section-label">📄 Plain English Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{summary}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">⚠️ Red Flags</div>', unsafe_allow_html=True)
        flag_class = "flag-box" if "No significant" not in flags else "good-box"
        st.markdown(f'<div class="{flag_class}">{flags}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">✅ Action Items Before Closing</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{actions}</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="powered">Generated by ClearCommitment · AI-powered title review</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("ClearCommitment · AI-assisted title commitment review · Not a law firm · Always verify with a licensed title attorney.")