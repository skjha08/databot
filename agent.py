import sys
import asyncio

# In the Google ADK pattern, you import the Agent class from google.adk
from google.adk import Agent
from google.adk.runners import InMemoryRunner

# Import our Python functions to be used as tools
from tools import load_dataset, calculate_stats, check_missing_values, get_correlation

def extract_final_text(events) -> str:
    """Extracts the final text response from a list of ADK events."""
    for event in reversed(events):
        if getattr(event, "content", None) and getattr(event.content, "parts", None):
            texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if texts:
                return "".join(texts).strip()
    return str(events) # fallback if nothing found

async def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py <path_to_csv>")
        sys.exit(1)
        
    csv_filepath = sys.argv[1]
    
    # The instruction parameter enforces the behavior of the agent.
    instruction = """
    You are a DataBot, an AI data analyst. Your job is to analyze the user's dataset and output a clear plain-English summary of your findings.
    
    CRITICAL RULE: You MUST always call the `load_dataset` tool first before taking any other action or calling any other tools.
    
    Once the dataset is loaded, explore it using your available tools (like check_missing_values and calculate_stats).
    Finally, provide a concise, plain-English summary of the most interesting findings from the tools.
    """
    
    # Initialize the ADK Agent
    # We pass it the name, model, instruction, and the list of our raw Python functions.
    agent = Agent(
        name="DataBot",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[
            load_dataset,
            calculate_stats,
            check_missing_values,
            get_correlation
        ]
    )
    
    print(f"DataBot: Initializing analysis for {csv_filepath}...\n")
    
    # Instantiate an InMemoryRunner to execute the agent's logic programmatically
    runner = InMemoryRunner(agent=agent)
    
    try:
        # We invoke the agent asynchronously (verbose=True keeps the tool-call logging)
        events = await runner.run_debug(f"Please load and analyze this dataset: {csv_filepath}. Also check the correlation between Age and Fare", verbose=True)
        
        print("\n--- Final Summary ---")
        final_text = extract_final_text(events)
        print(final_text)
    except Exception as e:
        print(f"An error occurred while running the agent: {e}")

if __name__ == "__main__":
    asyncio.run(main())
