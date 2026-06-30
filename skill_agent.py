import sys
import asyncio
import os

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
    
    Once the procedure is complete, provide a concise summary.
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

async def main():
    if len(sys.argv) < 3:
        print("Usage: python skill_agent.py <path_to_csv> <query>")
        sys.exit(1)
        
    csv_filepath = sys.argv[1]
    query = " ".join(sys.argv[2:])
    
    skills = get_available_skills()
    if not skills:
        print("No skills found.")
        return
        
    print(f"Routing query: '{query}'")
    chosen_skill = await route_to_skill(query, skills)
    if chosen_skill:
        print(f"--> Selected Skill: {chosen_skill['name']}\n")
        print("Running specialist agent...")
        result = await run_with_skill(query, csv_filepath, chosen_skill)
        print("\n--- Final Summary ---")
        print(result)
    else:
        print("No appropriate skill found for the query.")

if __name__ == "__main__":
    asyncio.run(main())
