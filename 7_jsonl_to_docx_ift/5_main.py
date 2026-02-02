def main():
    if not os.path.exists(INPUT_DIR):
        print(f"⚠️ Input directory '{INPUT_DIR}' does not exist.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join(OUTPUT_BASE_DIR, timestamp)

    jsonl_files = []
    for root, _, files in os.walk(INPUT_DIR):
        for f in files:
            if f.lower().endswith(".jsonl"):
                jsonl_files.append(os.path.join(root, f))

    if not jsonl_files:
        print("⚠️ No JSONL files found.")
        return

    print("\n" + "-" * 30)
    print(f"🔄 Converting {len(jsonl_files)} file(s)...")

    total_converted = 0

    for file_path in tqdm(jsonl_files, desc="Converting", unit="file"):
        filename = os.path.basename(file_path)
        out_p = os.path.join(
            output_dir,
            filename.replace(".jsonl", ".docx")
        )

        try:
            total_converted += convert_jsonl_to_docx(file_path, out_p)
        except Exception as e:
            tqdm.write(f"⚠️ Error processing '{filename}': {e}")

    print("-" * 30)
    print(f"📝 Total restored examples:: {total_converted}")
    print(f"📂 Results saved in folder: docx_files")
    print("-" * 30)
    print("👋 Byee!")


if __name__ == "__main__":
    main()
