# DataBot v1.0 — Spec

## Inputs
- filepath: string, CSV file path
- query: string, natural language question, max 5000 chars

## Outputs
JSON: {status, skill_used, tools_called, answer, warnings}

## Behavior Rules
1. load_dataset MUST be called before any other tool
2. If filepath contains ".." or starts with "/", reject with status=error before touching tools
3. If query matches injection patterns, reject with status=error before routing
4. If a column has >30% missing values, warnings list MUST mention it
5. If no skill matches the query, status=error, skill_used="none"

## Out of Scope (v1.0)
- Model training execution (routing only, tools not yet built)
- Visualizations

