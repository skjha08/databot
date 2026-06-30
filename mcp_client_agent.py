import asyncio
import sys
import json
import os
from google import genai
from google.genai import types as genai_types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    if len(sys.argv) < 3:
        print("Usage: python mcp_client_agent.py <csv_filepath> <question>")
        sys.exit(1)
        
    csv_filepath = sys.argv[1]
    question = sys.argv[2]
    
    # In Windows, we need to ensure the env is passed correctly or sys.executable is used
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["databot_mcp_server.py"],
        env=os.environ.copy()
    )
    
    print("Connecting to MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools_response = await session.list_tools()
            tools_list = tools_response.tools
            
            print("\n--- Discovered Tools ---")
            for t in tools_list:
                print(f"- {t.name}: {t.description}")
            print("------------------------\n")
            
            # 1. Load the dataset
            print(f"Loading dataset {csv_filepath}...")
            load_result = await session.call_tool("load_dataset", {"filepath": csv_filepath})
            print("Load result:", load_result.content[0].text)
            
            # 2. Ask Gemini which tool to use
            client = genai.Client()
            
            tools_prompt = "Available tools:\n"
            for t in tools_list:
                if t.name == "load_dataset":
                    continue # already called
                tools_prompt += f"- {t.name}: {t.description}\n"
                tools_prompt += f"  Schema: {json.dumps(t.inputSchema)}\n"
                
            prompt = f"""
You are an AI assistant. You have access to the following tools:
{tools_prompt}

The dataset has already been loaded. The user's question is: "{question}"

Which single tool should you call to answer this question? 
Provide your answer as a JSON object with two keys: "tool" (the name of the tool) and "arguments" (a dictionary of arguments).
Do not provide any other text.
"""
            
            print(f"\nAsking Gemini which tool to call for: '{question}'...")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            try:
                plan = json.loads(response.text)
                tool_name = plan.get("tool")
                tool_args = plan.get("arguments", {})
                
                print(f"Gemini chose to call: {tool_name} with args {tool_args}")
                
                # 3. Execute the tool
                tool_result = await session.call_tool(tool_name, tool_args)
                raw_result = tool_result.content[0].text
                
                print("\nRaw Tool Result:")
                print(raw_result)
                print("-" * 20)
                
                # 4. Synthesize final answer
                synth_prompt = f"""
The user asked: "{question}"
We called the tool '{tool_name}' and got the following result:
{raw_result}

Please provide a plain-English, conversational answer to the user based on this result.
"""
                synth_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=synth_prompt
                )
                
                print("\nFinal Answer:")
                print(synth_response.text)
                
            except json.JSONDecodeError:
                print("Failed to parse Gemini response as JSON:")
                print(response.text)
            except Exception as e:
                print(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
