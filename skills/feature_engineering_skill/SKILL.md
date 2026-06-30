---
name: feature_engineering_skill
description: Use this skill for feature engineering. Triggers when the user asks to "prepare data", "encode", "handle missing", or "transform". Do NOT use for EDA or model training.
---
# Feature Engineering Procedure
Decision tree for handling missing values and encoding categoricals:
- If numeric column has <5% missing values, drop rows.
- If numeric column has >5% missing values, impute with median.
- If categorical column has missing values, impute with mode.
- For categoricals with low cardinality (<5 unique values), use One-Hot Encoding.
- For categoricals with high cardinality (>=5 unique values), use Target Encoding or drop if unimportant.
