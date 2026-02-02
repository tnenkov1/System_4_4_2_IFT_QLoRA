def call_ollama(text, prompt_template, session):
    """Sends a request to Ollama to translate a specific text element."""
    if not text.strip() or len(text.strip()) < 2:
        return text
    
    if "{text}" in prompt_template:
        full_prompt = prompt_template.replace("{text}", text)
    else:
        full_prompt = f"{prompt_template}\n\nText: {text}"
    
    try:
        payload = {"model": MODEL, "prompt": full_prompt, "stream": False}
        r = session.post(API_URL, json=payload, timeout=180)
        return r.json().get("response", "").strip()
    except Exception as e:
        write_log(f"API Error: {str(e)}")
        return text