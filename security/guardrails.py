def validate_input(text: str) -> tuple[bool, str]:
    """
    Validates user input to block prompt injections and overly long inputs.
    """
    if len(text) > 5000:
        return False, "Input exceeds 5000 characters."
    
    text_lower = text.lower()
    blocked_phrases = [
        "ignore previous instructions",
        "you are now",
        "reveal your system prompt"
    ]
    
    for phrase in blocked_phrases:
        if phrase in text_lower:
            return False, f"Prompt injection detected: '{phrase}'."
            
    return True, "Safe"

def validate_tool_call(tool_name: str, args: dict) -> tuple[bool, str]:
    """
    Validates arguments passed to a tool. Specifically protects filepaths.
    """
    if tool_name == "load_dataset":
        filepath = args.get("filepath", "")
        if ".." in filepath:
            return False, "Directory traversal detected (.. in filepath)."
        if filepath.startswith("/"):
            return False, "Absolute root paths (/) are not allowed."
            
    return True, "Safe"
