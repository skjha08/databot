# DataBot v0.1

DataBot is a CLI AI agent designed to perform automated data analysis on CSV files. It leverages Google's Agent Development Kit (ADK) to understand the dataset's structure, identify missing values, calculate summary statistics, and find correlations between features. It wraps this analysis into a clear, plain-English summary, saving time on exploratory data analysis.

## Tech Stack
- **Python**: Core programming language.
- **Google ADK**: Used to orchestrate the AI agent and tools.
- **Gemini**: The underlying Language Model powering the agent's reasoning.
- **Pandas**: Used for robust data manipulation.

## Setup Instructions

1. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install google-adk pandas
   ```

3. **Set your Google API Key:**
   You must set your Gemini API key as an environment variable before running the bot.
   ```bash
   # On Windows (Command Prompt):
   set GOOGLE_API_KEY=your_api_key_here
   # On macOS/Linux:
   export GOOGLE_API_KEY=your_api_key_here
   ```
   *(Alternatively, you can create a `.env` file in the root directory and place your key there.)*

## How to Run

Execute the agent by providing the path to a CSV file (e.g., `_titanic.csv`):
```bash
python agent.py _titanic.csv
```

## The Agent Loop (Thought → Action → Observation)

The DataBot operates using the standard agentic loop provided by the Google ADK:
1. **Thought:** The model processes the initial prompt and recognizes it must first load the data.
2. **Action:** It calls the `load_dataset` tool from `tools.py`.
3. **Observation:** The tool executes in Python, caching the dataset in memory, and returns a success message to the agent.
4. The loop repeats: The agent thinks about what to do next, subsequently calling `calculate_stats` or `check_missing_values` to gather data. Finally, it might use `get_correlation` to explore specific relationships, before synthesizing all its observations into a final response.
