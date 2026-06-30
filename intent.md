# DataBot v0.1 — Intent

Build a CLI AI agent using Google ADK that:
- Takes a CSV filepath as input
- Has 4 tools: load_dataset, calculate_stats, check_missing_values, get_correlation
- Uses the standard agent loop (model decides which tool to call, tool executes, result fed back, repeat until final answer)
- System prompt: agent must ALWAYS call load_dataset first before anything else
- Output: a clear plain-English summary of findings

Use Google ADK's Agent and Tool classes, not raw genai.GenerativeModel calls.
Keep tools.py separate from agent.py.
