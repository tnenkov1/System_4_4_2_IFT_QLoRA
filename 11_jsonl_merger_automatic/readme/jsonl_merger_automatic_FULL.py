import os
import json
import re
import glob
from datetime import datetime
from tqdm import tqdm

INPUT_FOLDER = "jsonl_files"
OUTPUT_FOLDER = "jsonl_merged_files"
MODEL_NAME = "dataset"

def safe_json_load(line):
    """Attempts to fix common JSON errors in a line."""
    line = line.replace("\u0000", "").strip()
    if "'" in line and '"' not in line:
        line = re.sub(r"'", '"', line)
    if line and not line.endswith("}"):
        line += "}"
    try:
        return json.loads(line)
    except:
        return None

def ift_record(data):
    """Converts the record into a clean IFT format."""
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

def process_and_merge():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_folder = os.path.join(base_dir, INPUT_FOLDER)
    out_folder = os.path.join(base_dir, OUTPUT_FOLDER)
    os.makedirs(out_folder, exist_ok=True)

    jsonl_files = glob.glob(os.path.join(root_folder, "**", "*.jsonl"), recursive=True)
    jsonl_files = sorted(jsonl_files, key=lambda x: os.path.basename(x).lower())

    if not jsonl_files:
        print(f"❌ Не бяха намерени .jsonl файлове в '{root_folder}'")
        return

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_path = os.path.join(out_folder, f"{MODEL_NAME}_{timestamp}_merged.jsonl")

    stats = {"total_lines": 0, "repaired_json": 0, "written_records": 0}
    total_size = sum(os.path.getsize(f) for f in jsonl_files)

    print(f"🔍 Found files: {len(jsonl_files)}")
    print(f"📂 Target file: {output_path}\n")

    is_first_record = True

    with open(output_path, 'w', encoding='utf-8') as outfile, \
         tqdm(total=total_size, unit='B', unit_scale=True, desc="Progress") as pbar:
        
        for file_path in jsonl_files:
            with open(file_path, 'r', encoding='utf-8') as infile:
                for line in infile:
                    raw_line = line.strip()
                    if not raw_line:
                        pbar.update(len(line.encode('utf-8')))
                        continue
                    
                    stats["total_lines"] += 1
                    
                    try:
                        data = json.loads(raw_line)
                    except:
                        data = safe_json_load(raw_line)
                        if data:
                            stats["repaired_json"] += 1
                        else:
                            data = {}

                    record = ift_record(data)

                    if any(record.values()):
                        json_string = json.dumps(record, ensure_ascii=False)
                        
                        if is_first_record:
                            outfile.write(json_string)
                            is_first_record = False
                        else:
                            outfile.write("\n" + json_string)
                        
                        stats["written_records"] += 1
                    
                    pbar.update(len(line.encode('utf-8')))

    print("\n" + "="*30)
    print("📊 FINAL STATISTICS:")
    print(f"📄 Total lines read: {stats['total_lines']}")
    print(f"🛠 JSON objects repaired: {stats['repaired_json']}")
    print(f"✅ Valid records: {stats['written_records']}")
    print("="*30)

if __name__ == "__main__":
    process_and_merge()
