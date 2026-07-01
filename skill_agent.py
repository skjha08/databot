import sys
import asyncio
import os
import json

# Google ADK imports
from google.adk import Agent
from google.adk.runners import InMemoryRunner

# Import tools
from tools import load_dataset, calculate_stats, check_missing_values, get_correlation

def get_available_skills():
    """Reads SKILL.md files in subdirectories and parses their frontmatter."""
    skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
    skills = []
    for d in os.listdir(skills_dir):
        skill_dir_path = os.path.join(skills_dir, d)
        skill_path = os.path.join(skill_dir_path, "SKILL.md")
        if os.path.isdir(skill_dir_path) and os.path.exists(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                name = None
                desc = None
                
                # Simple parsing of YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---")
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        for line in frontmatter.split('\n'):
                            if line.startswith('name:'):
                                name = line.split('name:', 1)[1].strip()
                            elif line.startswith('description:'):
                                desc = line.split('description:', 1)[1].strip()
                        if name and desc:
                            skills.append({
                                "name": name,
                                "description": desc,
                                "path": skill_path,
                                "content": content
                            })
    return skills

def extract_final_text(events) -> str:
    """Extracts the final text response from a list of ADK events."""
    for event in reversed(events):
        if getattr(event, "content", None) and getattr(event.content, "parts", None):
            texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if texts:
                return "".join(texts).strip()
    return str(events) # fallback if nothing found

def parse_agent_response(text: str, skill_name: str = "unknown") -> dict:
    """Parses JSON from the agent, falling back to a structured error if parsing fails."""
    try:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        return json.loads(clean_text.strip())
    except Exception as e:
        return {
            "status": "error",
            "skill_used": skill_name,
            "tools_called": [],
            "answer": f"Failed to parse agent output.",
            "warnings": [f"Parse error: {str(e)}", f"Raw output: {text[:200]}"]
        }

async def route_to_skill(query, skills):
    """Uses a routing agent to pick the best skill based on descriptions."""
    prompt = f"Given the user query: '{query}', which of the following skills is the most appropriate? Return ONLY the exact skill name, nothing else.\n\n"
    for s in skills:
        prompt += f"Skill: {s['name']}\nDescription: {s['description']}\n\n"
        
    router_agent = Agent(
        name="Router",
        model="gemini-2.5-flash",
        instruction="You are a routing agent. You must output only the exact name of the best matching skill."
    )
    runner = InMemoryRunner(agent=router_agent)
    events = await runner.run_debug(prompt, verbose=False)
    chosen_skill_name = extract_final_text(events).strip()
    
    for s in skills:
        if s['name'] == chosen_skill_name:
            return s
    return None

async def run_with_skill(query, csv_filepath, skill):
    """Runs the ADK agent using the chosen skill's full content as instructions."""
    instruction = f"""
    You are a DataBot, an AI data analyst. Your job is to fulfill the user query.
    
    CRITICAL RULE: You MUST always call the `load_dataset` tool first before taking any other action or calling any other tools.
    
    Here is the specific procedure you must follow (from {skill['name']}):
    {skill['content']}
    
    Once the procedure is complete, you MUST output a JSON response matching this schema exactly. Do not output anything else besides this JSON block:
    {{
      "status": "success",
      "skill_used": "{skill['name']}",
      "tools_called": ["list", "of", "tool names", "you", "called"],
      "answer": "your concise summary of the result",
      "warnings": ["any warnings, such as columns with >30% missing values"]
    }}
    """
    
    agent = Agent(
        name="DataBot_Specialist",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[
            load_dataset,
            calculate_stats,
            check_missing_values,
            get_correlation
        ]
    )
    
    runner = InMemoryRunner(agent=agent)
    events = await runner.run_debug(f"Query: {query}\nDataset: {csv_filepath}", verbose=True)
    return extract_final_text(events)

import sys
import os

# Add the project root to the python path so we can import security.guardrails
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from security.guardrails import validate_input

async def main():
    if len(sys.argv) < 3:
        print(json.dumps({"status": "error", "skill_used": "none", "tools_called": [], "answer": "Usage: python skill_agent.py <path_to_csv> <query>", "warnings": []}))
        sys.exit(1)
        
    csv_filepath = sys.argv[1]
    query = " ".join(sys.argv[2:])
    
    is_safe, reason = validate_input(query)
    if not is_safe:
        print(json.dumps({"status": "error", "skill_used": "none", "tools_called": [], "answer": f"Security violation - {reason}", "warnings": []}))
        return

    skills = get_available_skills()
    if not skills:
        print(json.dumps({"status": "error", "skill_used": "none", "tools_called": [], "answer": "No skills found.", "warnings": []}))
        return
        
    chosen_skill = await route_to_skill(query, skills)
    if chosen_skill:
        result_text = await run_with_skill(query, csv_filepath, chosen_skill)
        result_json = parse_agent_response(result_text, chosen_skill['name'])
        print(json.dumps(result_json))
    else:
        print(json.dumps({"status": "error", "skill_used": "none", "tools_called": [], "answer": "No appropriate skill found for the query.", "warnings": []}))

if __name__ == "__main__":
    asyncio.run(main())
