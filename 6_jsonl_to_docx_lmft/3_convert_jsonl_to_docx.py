def convert_jsonl_to_docx(input_path, output_path):
    """Converts a JSONL file back into a DOCX document structure."""
    doc = Document()

    examples_count = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                prompt = data.get("prompt", "")
                completion = data.get("completion", "")

                if prompt:
                    # Add prompt as Heading level 1
                    doc.add_heading(prompt, level=1)

                if completion:
                    # Add completion as a regular paragraph
                    doc.add_paragraph(completion)

                examples_count += 1
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue

    if examples_count > 0:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)

    return examples_count