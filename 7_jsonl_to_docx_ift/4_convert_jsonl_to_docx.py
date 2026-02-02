def convert_jsonl_to_docx(input_path, output_path):
    """Convert JSONL (instruction/input/output) to DOCX with 1.15 spacing only"""
    if not os.path.exists(input_path):
        return 0

    doc = Document()
    examples_count = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                instruction = data.get("instruction", "").strip()
                input_text = data.get("input", "").strip()
                output_text = data.get("output", "").strip()

                if instruction:
                    add_heading_115(doc, instruction)

                if input_text:
                    add_paragraph_115(doc, f"// {input_text}")

                if output_text:
                    add_paragraph_115(doc, output_text)

                add_paragraph_115(doc, "")

                examples_count += 1

            except json.JSONDecodeError:
                continue

    if examples_count > 0:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)

    return examples_count
