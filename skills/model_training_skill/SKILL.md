---
name: model_training_skill
description: Use this skill for training models. Triggers when the user asks to "train a model", "predict", or "classification". Do NOT use for EDA or feature engineering.
---
# Model Training Procedure
Algorithm selection guide:
- For binary classification, start with Logistic Regression or Random Forest.
- For regression, start with Linear Regression or Gradient Boosting.

Procedure:
1. Ensure the dataset is loaded and preprocessed.
2. Perform a train/test split (e.g., 80/20 split).
3. Select an appropriate algorithm based on the guide above.
4. Set up cross-validation (e.g., 5-fold CV) to evaluate the model reliably.
5. Report the evaluation metrics (accuracy, F1-score, or RMSE).
