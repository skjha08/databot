# DataBot Spec-Driven Production — Intent

Goal: generate production code FROM the existing specs/databot_spec.md, and add a 
policy layer + CI gate.

1. Create specs/databot_bdd.md
   - 4 Gherkin-style scenarios (Given/When/Then) covering: happy path EDA, blocked 
     directory traversal, blocked prompt injection, missing-value warning trigger
   - Base these directly on databot_spec.md's behavior rules

2. Create security/policy_server.py
   - Wraps the existing guardrails.py with role-based tool permissions (use a 
     simple dict, not full YAML): role "viewer" can only use load_dataset, 
     calculate_stats, check_missing_values, get_correlation; no other roles needed yet
   - check_tool_call(tool_name, args, role) -> (allowed: bool, reason: str)
   - This sits in front of skill_agent.py's tool execution as an additional layer 
     beyond guardrails.py

3. Update skill_agent.py to return a structured dict matching the Output spec in 
   databot_spec.md (status, skill_used, tools_called, answer, warnings) instead of 
   just a raw string

4. Create .github/workflows/eval_gate.yml
   - A GitHub Actions workflow that runs evals/eval_runner.py on every push
   - Fails the build if pass rate is below 80%
   - Note: this needs GOOGLE_API_KEY as a GitHub secret, explain how to add that 
     in the walkthrough

Reference specs/databot_spec.md directly while generating — every behavior rule in 
the spec must be implemented exactly as written, not approximated.

