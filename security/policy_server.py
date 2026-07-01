from .guardrails import validate_tool_call

def check_tool_call(tool_name: str, args: dict, role: str) -> tuple[bool, str]:
    """
    Wraps the existing guardrails.py with role-based tool permissions.
    """
    if role == "viewer":
        allowed_tools = {"load_dataset", "calculate_stats", "check_missing_values", "get_correlation"}
        if tool_name not in allowed_tools:
            return False, f"Role '{role}' is not permitted to use tool '{tool_name}'."
            
    # Pass through to existing guardrails for filepath validation
    return validate_tool_call(tool_name, args)
