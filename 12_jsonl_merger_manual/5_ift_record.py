def ift_record(data):
    """Normalizes records to instruction/input/output format."""
    instruction = data.get("instruction", "")
    input_text = data.get("input", "")
    output = data.get("output", "")

    if not instruction and "prompt" in data:
        instruction = data["prompt"]
    if not output and "completion" in data:
        output = data["completion"]

    return {
        "instruction": str(instruction).strip(),
        "input": str(input_text).strip(),
        "output": str(output).strip()
    }