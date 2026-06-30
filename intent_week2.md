# DataBot MCP Server — Intent

Goal: expose the existing tools (load_dataset, calculate_stats, check_missing_values, 
get_correlation from tools.py) as a real MCP server, so any MCP-compatible client can 
discover and call them — not just our own agent.

Build two files:

1. databot_mcp_server.py
   - Uses the `mcp` Python SDK
   - Registers all 4 functions from tools.py as MCP tools with proper input schemas
   - Runs as a stdio server (so it can be launched as a subprocess by a client)

2. mcp_client_agent.py
   - Connects to databot_mcp_server.py as a subprocess via stdio
   - On startup, calls list_tools() and prints what tools were discovered (proves 
     dynamic discovery is working, not hardcoded)
   - Takes a CSV filepath and a natural language question as CLI args
   - Asks Gemini which MCP tool to call based on the question + discovered tool list
   - Executes that tool through the MCP session, prints the raw result
   - Then asks Gemini to synthesize a plain-English answer from that result

Use the real, current `mcp` Python SDK API — search current documentation if unsure of 
class names (StdioServerParameters, ClientSession, etc.) rather than guessing.

