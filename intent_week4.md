# DataBot Security & Evaluation — Intent

Goal: harden DataBot against bad input and build a way to test it that works for 
non-deterministic agents (normal unit tests don't work here).

1. Create security/guardrails.py
   - validate_input(text): block prompt injection patterns (e.g. "ignore previous 
     instructions", "you are now", "reveal your system prompt") and reject inputs 
     over 5000 chars
   - validate_tool_call(tool_name, args): block any filepath argument containing 
     ".." or starting with "/" (directory traversal protection)
   - Both functions return (is_safe: bool, reason: str)
   - This should wrap around the existing skill_agent.py flow — validate the user's 
     query before routing, validate any filepath argument before tools execute

2. Create evals/eval_runner.py
   - Define 3 test cases as a list of dicts: each has a query, a filepath, an 
     expected_skill (which skill SHOULD get selected), and keywords the final 
     answer should contain
   - One test case must be: query="../../etc/passwd", expect it to be BLOCKED by 
     guardrails before reaching the agent at all
   - Run all 3 cases against skill_agent.py, print pass/fail for each, print a 
     final pass rate

Wire guardrails.py into skill_agent.py: validate the query before routing, and 
validate the filepath before passing it to load_dataset.

