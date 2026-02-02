def load_prompt_text(filename):
    """Reads the content of a prompt file from the prompts folder."""
    path = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None