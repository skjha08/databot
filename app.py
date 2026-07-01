"""
app.py — DataBot Streamlit Frontend
=====================================
Run with:  streamlit run app.py

This file is a pure UI layer. All agent logic lives in skill_agent.py.
We import three things and nothing else from the backend:
  • run_with_skill   — executes the chosen skill against the CSV
  • route_to_skill   — uses the routing agent to pick the best skill
  • validate_input   — guardrail that blocks prompt-injection strings
"""

# ── Standard library ──────────────────────────────────────────────────────────
import asyncio
import tempfile
import os
import json

# ── Streamlit ─────────────────────────────────────────────────────────────────
# `import streamlit as st` is the universal first line of every Streamlit app.
# The `st` alias gives you the entire Streamlit API (widgets, layout, state…).
import streamlit as st

# ── Backend imports (no new logic — just wiring) ──────────────────────────────
from skill_agent import run_with_skill, route_to_skill, get_available_skills, parse_agent_response
from security.guardrails import validate_input


# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
# st.set_page_config() MUST be the very first Streamlit call in the script.
# It sets the browser tab title, icon, and layout width.
# layout="wide" stretches the app across the full browser window.
st.set_page_config(
    page_title="DataBot — AI Data Analyst",
    page_icon="🤖",
    layout="wide",
)


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS  (optional polish — purely cosmetic)
# ══════════════════════════════════════════════════════════════════════════════
# st.markdown() with unsafe_allow_html=True lets you inject raw HTML/CSS.
# We use it here just to tighten spacing; all logic uses proper st.* widgets.
st.markdown(
    """
    <style>
        /* Give the main content area a max width so it doesn't stretch too wide */
        .block-container { max-width: 860px; padding-top: 2rem; }
        /* Style the status badge spans */
        .badge-success { color: #1a9e5c; font-weight: 700; font-size: 1.05rem; }
        .badge-error   { color: #d94f4f; font-weight: 700; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER  — st.title / st.caption
# ══════════════════════════════════════════════════════════════════════════════
# st.title() renders an <h1> element. Streamlit auto-applies its theme font.
# st.caption() renders smaller, muted helper text below the title.
st.title("🤖 DataBot — AI Data Analyst")
st.caption(
    "Upload a CSV, ask a question in plain English, and DataBot will route "
    "your query to the right analysis skill."
)

st.divider()  # st.divider() draws a horizontal rule — purely decorative


# ══════════════════════════════════════════════════════════════════════════════
# FILE UPLOADER  — st.file_uploader
# ══════════════════════════════════════════════════════════════════════════════
# st.file_uploader() renders a drag-and-drop upload zone.
#   • label          — the visible prompt text
#   • type           — list of allowed extensions (Streamlit enforces this in UI)
#   • help           — small tooltip shown on hover
# The widget returns None when nothing is uploaded, or a UploadedFile object.
uploaded_file = st.file_uploader(
    label="📂 Upload your CSV dataset",
    type=["csv"],
    help="Only .csv files are accepted.",
)


# ══════════════════════════════════════════════════════════════════════════════
# TEXT INPUT  — st.text_input
# ══════════════════════════════════════════════════════════════════════════════
# st.text_input() renders a single-line text box.
#   • label          — prompt text above the box
#   • placeholder    — greyed-out hint inside the box when empty
#   • max_chars      — enforces the same 5000-char limit as validate_input()
# The widget returns whatever the user has typed (empty string by default).
question = st.text_input(
    label="💬 Ask a question about your data",
    placeholder="e.g. What are the top correlating features? Any missing values?",
    max_chars=5000,
)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYZE BUTTON  — st.button
# ══════════════════════════════════════════════════════════════════════════════
# st.button() renders a clickable button.
# It returns True only on the specific re-run caused by the click; otherwise False.
# This means ALL the code inside `if analyze:` runs exactly once per click,
# then Streamlit re-renders the page and the button goes back to False.
analyze = st.button("🔍 Analyze", type="primary", use_container_width=True)
# type="primary"          → blue accent color matching the theme's call-to-action
# use_container_width=True → stretches the button to the full column width


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS LOGIC  (runs only when the button is clicked)
# ══════════════════════════════════════════════════════════════════════════════
if analyze:

    # ── Input validation (UI-level, before touching the agent) ────────────────

    # Guard 1: no file uploaded
    if uploaded_file is None:
        # st.error() renders a red alert box. We never show raw tracebacks —
        # all errors are routed through st.error() or st.warning().
        st.error("⚠️ Please upload a CSV file first.")
        st.stop()  # st.stop() halts the rest of the script for this run

    # Guard 2: empty question
    if not question.strip():
        st.error("⚠️ Please enter a question.")
        st.stop()

    # Guard 3: security guardrail on the question text
    # validate_input() returns (bool, reason_string)
    is_safe, reason = validate_input(question)
    if not is_safe:
        st.error(f"🚫 Rejected by security policy: {reason}")
        st.stop()

    # Guard 4: reject non-.csv filenames at the Python level too
    # (Streamlit's type filter handles the UI, but defence-in-depth is good practice)
    if not uploaded_file.name.lower().endswith(".csv"):
        st.error("🚫 Only .csv files are supported.")
        st.stop()

    # Guard 5: validate the filename itself through guardrails
    filename_safe, filename_reason = validate_input(uploaded_file.name)
    if not filename_safe:
        st.error(f"🚫 Filename rejected by security policy: {filename_reason}")
        st.stop()

    # ── Save uploaded bytes to a temp file ───────────────────────────────────
    # Streamlit's UploadedFile is an in-memory bytes object, not a disk path.
    # The agent needs a real filepath, so we write it to a NamedTemporaryFile.
    # delete=False means the file persists after the `with` block closes — we
    # delete it manually in the `finally` clause below.
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False
        ) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        # ── Spinner while the agent runs ─────────────────────────────────────
        # st.spinner() shows an animated loading indicator while the indented
        # block executes. The message is shown next to the spinner icon.
        with st.spinner("🤖 DataBot is thinking… routing to the best skill…"):
            try:
                # Load skills, pick the best one, then run it — all async.
                # Because Streamlit's main thread is synchronous, we wrap each
                # async call with asyncio.run() which blocks until it completes.
                skills = get_available_skills()
                if not skills:
                    st.error("No skills found. Check your skills/ directory.")
                    st.stop()

                chosen_skill = asyncio.run(route_to_skill(question, skills))
                if chosen_skill is None:
                    st.error("Could not route to any skill. Try rephrasing your question.")
                    st.stop()

                raw_text = asyncio.run(
                    run_with_skill(question, tmp_path, chosen_skill)
                )
                result = parse_agent_response(raw_text, chosen_skill["name"])

            # ── Specific API errors ───────────────────────────────────────────
            except Exception as exc:
                err_str = str(exc)
                if "429" in err_str:
                    st.error(
                        "🚦 API limit reached. Please wait a minute and try again."
                    )
                elif "503" in err_str:
                    st.error(
                        "⚙️ Gemini is experiencing high load. Please try again shortly."
                    )
                else:
                    # Trim the message — never expose full stack traces in the UI
                    brief = err_str[:200]
                    st.error(f"❌ Something went wrong: {brief}")
                st.stop()

        # ══════════════════════════════════════════════════════════════════════
        # RESULTS SECTION  (only visible after a successful analysis run)
        # ══════════════════════════════════════════════════════════════════════

        st.divider()
        st.subheader("📊 Results")
        # st.subheader() renders an <h3>; sits between st.title() and st.header()

        # ── Row of metric cards ───────────────────────────────────────────────
        # st.columns(n) splits the row into n equal-width columns.
        # Each column is used as a context manager: `with col1:` scopes widgets
        # to that column. Columns are the primary layout tool in Streamlit.
        col1, col2, col3 = st.columns(3)

        with col1:
            # st.metric() renders a card with a large value and a label above it.
            # Perfect for KPIs/summary numbers.
            st.metric(
                label="🧠 Skill Selected",
                value=result.get("skill_used", "unknown"),
            )

        with col2:
            tools_called = result.get("tools_called", [])
            st.metric(
                label="🛠 Tools Called",
                value=len(tools_called),
            )

        with col3:
            status = result.get("status", "unknown")
            # We emit raw HTML for the coloured badge via st.markdown().
            # All other content uses standard widgets — this is the exception.
            if status == "success":
                st.markdown(
                    '<p>✅ Status<br><span class="badge-success">SUCCESS</span></p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p>❌ Status<br><span class="badge-error">ERROR</span></p>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # ── Main answer ───────────────────────────────────────────────────────
        # st.text_area() renders a multi-line, scrollable read-only box when
        # disabled=True. It's ideal for displaying potentially long text output.
        st.text_area(
            label="💡 Answer",
            value=result.get("answer", "No answer returned."),
            height=200,
            disabled=True,  # read-only; user can still select/copy text
        )

        # ── Warnings ─────────────────────────────────────────────────────────
        # st.warning() renders a yellow alert box.
        # We only render the section if there are actual warnings to display.
        warnings = result.get("warnings", [])
        if warnings:
            st.markdown("**⚠️ Warnings**")
            for w in warnings:
                # Each warning gets its own st.warning() box so they stack
                # vertically as distinct callouts — easy to scan.
                st.warning(w)

        # ── Raw JSON expander ─────────────────────────────────────────────────
        # st.expander() collapses its children behind a clickable toggle.
        # Great for "advanced" or "technical" content that clutters the main view.
        # expanded=False means it starts collapsed.
        with st.expander("🔎 Raw JSON output (for transparency)", expanded=False):
            # st.json() pretty-prints a dict/list as syntax-highlighted JSON.
            # It's more readable than st.code(json.dumps(…)) for nested objects.
            st.json(result)

    finally:
        # Always clean up the temp file, even if an error occurred mid-run.
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
