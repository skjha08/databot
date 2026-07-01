import pandas as pd

# Global variable to cache the DataFrame
# The agent will only need to call load_dataset once, and the data will be reused!
_GLOBAL_DF = None

import sys
import os

# Add the project root to the python path so we can import security.policy_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from security.policy_server import check_tool_call

def load_dataset(filepath: str) -> str:
    """
    Loads a CSV dataset from the specified filepath into memory.
    This MUST be called before any other tool.
    
    Args:
        filepath: The path to the CSV file to load.
        
    Returns:
        A string indicating success or failure.
    """
    is_safe, reason = check_tool_call('load_dataset', {'filepath': filepath}, 'viewer')
    if not is_safe:
        return f"Error loading dataset: Security violation - {reason}"
        
    global _GLOBAL_DF
    try:
        _GLOBAL_DF = pd.read_csv(filepath)
        return f"Successfully loaded dataset with {_GLOBAL_DF.shape[0]} rows and {_GLOBAL_DF.shape[1]} columns."
    except Exception as e:
        return f"Error loading dataset: {str(e)}"

def calculate_stats() -> str:
    """
    Calculates and returns summary statistics of the loaded dataset.
    
    Returns:
        A string containing the summary statistics of numerical columns.
    """
    global _GLOBAL_DF
    is_safe, reason = check_tool_call('calculate_stats', {}, 'viewer')
    if not is_safe:
        return f"Error: Security violation - {reason}"
    if _GLOBAL_DF is None:
        return "Error: Dataset not loaded. Please call load_dataset first."
    
    return _GLOBAL_DF.describe().to_string()

def check_missing_values() -> str:
    """
    Checks the loaded dataset for missing values.
    
    Returns:
        A string showing the count of missing values for each column.
    """
    global _GLOBAL_DF
    is_safe, reason = check_tool_call('check_missing_values', {}, 'viewer')
    if not is_safe:
        return f"Error: Security violation - {reason}"
    if _GLOBAL_DF is None:
        return "Error: Dataset not loaded. Please call load_dataset first."
    
    missing = _GLOBAL_DF.isnull().sum()
    return missing[missing > 0].to_string() if missing.sum() > 0 else "No missing values found in the dataset."

def get_correlation(col1: str, col2: str) -> str:
    """
    Calculates the Pearson correlation coefficient between two specific columns.
    
    Args:
        col1: The name of the first column.
        col2: The name of the second column.
        
    Returns:
        A string containing the correlation result or an error message.
    """
    global _GLOBAL_DF
    is_safe, reason = check_tool_call('get_correlation', {'col1': col1, 'col2': col2}, 'viewer')
    if not is_safe:
        return f"Error: Security violation - {reason}"
    if _GLOBAL_DF is None:
        return "Error: Dataset not loaded. Please call load_dataset first."
    
    if col1 not in _GLOBAL_DF.columns or col2 not in _GLOBAL_DF.columns:
        return f"Error: One or both columns '{col1}', '{col2}' not found in dataset."
        
    try:
        corr = _GLOBAL_DF[col1].corr(_GLOBAL_DF[col2])
        return f"The correlation between {col1} and {col2} is {corr:.4f}"
    except Exception as e:
        return f"Error calculating correlation: {str(e)}"
