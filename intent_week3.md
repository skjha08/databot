# DataBot Agent Skills — Intent

Goal: build a skill router so DataBot becomes a specialist on demand, based on what 
the user asks, without writing new code for each specialization.

1. Create skills/eda_skill/SKILL.md
   - YAML frontmatter with: name, description (must state WHEN to use and WHEN NOT 
     to use this skill — this is how the router picks it)
   - Step-by-step procedure: load_dataset first, then check_missing_values, then 
     calculate_stats on numeric columns, then summarize with a "Readiness Score" 1-10

2. Create skills/feature_engineering_skill/SKILL.md
   - Description: triggers on "prepare data", "encode", "handle missing", "transform"
   - Decision tree for handling missing values and encoding categoricals (don't run 
     code, just give the agent a documented decision procedure)

3. Create skills/model_training_skill/SKILL.md
   - Description: triggers on "train a model", "predict", "classification"
   - Algorithm selection guide + train/test split + cross-validation procedure

4. Create skill_agent.py
   - route_to_skill(query): asks Gemini which skill fits, based on reading all 3 
     SKILL.md descriptions (not the full bodies — just descriptions, to save tokens)
   - run_with_skill(query, filepath): loads the chosen SKILL.md's full content into 
     context, then runs the existing ADK agent (reuse agent.py's Agent + tools) with 
     that skill's procedure as additional instruction
   - Print which skill was selected before running, so the routing decision is visible

Reuse the existing tools.py functions — don't duplicate tool logic inside skills.

