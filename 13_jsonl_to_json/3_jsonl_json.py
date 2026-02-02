def jsonl_to_json():
    jsonl_files = glob.glob(os.path.join(INPUT_DIR, "*.jsonl"))

    if not jsonl_files:
        print(f"⚠️ No .jsonl files found in '{INPUT_DIR}'")
        return

    print(f"🔍 Found {len(jsonl_files)} files for conversion.\n")

    for file_path in jsonl_files:
        # 1. Generate timestamp (date_time)
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        
        # 2. Process file names
        filename = os.path.basename(file_path)        
        name_no_ext = os.path.splitext(filename)[0]   
        
        output_name = f"{name_no_ext}_{timestamp}.json"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    data.append(obj)
                except json.JSONDecodeError as e:
                    print(f"❌ Error in {filename} at line {line_number}: {e}")
                    continue

        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(data, f_out, ensure_ascii=False, indent=4)

        print(f"✅ The file is converted: {filename} -> {output_name}")

if __name__ == "__main__":
    jsonl_to_json()
    print(f"\n✨ Conversion finished. Results are in: json_files")
