---
name: eda_skill
description: Use this skill for exploratory data analysis (EDA). Triggers when the user asks to "explore", "summarize", "describe", or get a "readiness score" for the dataset. Do NOT use for model training or feature engineering.
---
# EDA Procedure
1. Call `load_dataset` to load the target CSV file.
2. Call `check_missing_values` to assess data quality.
3. Call `calculate_stats` on numeric columns to understand distributions.
4. Summarize the findings.
5. Provide a "Readiness Score" from 1-10 based on how clean the dataset looks.
