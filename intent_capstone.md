# DataBot Capstone — Streamlit App Intent

## Goal
Wrap the existing DataBot backend into a browser UI using Streamlit.
The app connects directly to skill_agent.py — no new agent logic,
no new tools, just a clean frontend over what already exists.

## UI Layout (single page)
1. Header: "DataBot — AI Data Analyst"
2. File uploader: accepts .csv files only
3. Text input: "Ask a question about your data"
4. Analyze button: triggers the agent
5. Results section (only visible after analysis runs):
   - Metric: which skill was selected (eda_skill, feature_engineering_skill etc)
   - Metric: how many tools were called
   - Success/error status badge
   - Main answer in a text box
   - Warnings as yellow warning boxes (st.warning) if warnings list is non-empty
   - Expander showing raw JSON output for transparency

## Backend Integration
- On button click: save uploaded file to a temp path using tempfile.NamedTemporaryFile
- Call run_with_skill() from skill_agent.py directly (import it)
- Pass the temp filepath and user question
- Since run_with_skill is async, wrap it with asyncio.run()
- Parse the returned JSON dict and render each field as described above

## Error Handling (show these as st.error, never show raw tracebacks)
- No file uploaded → "Please upload a CSV file first"
- Empty question → "Please enter a question"
- API quota error (429) → "API limit reached. Please wait a minute and try again."
- Server error (503) → "Gemini is experiencing high load. Please try again shortly."
- Any other exception → "Something went wrong: {brief error message}"

## Security
- Validate the uploaded filename through existing guardrails.validate_input()
  before passing to the agent
- Reject non-.csv files before saving them

## File
- Single file: app.py in the databot root
- Run with: streamlit run app.py

