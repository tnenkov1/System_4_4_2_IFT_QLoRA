import os
import json
import re
import glob
from datetime import datetime
from tqdm import tqdm

# Write manually the file names
FILES_TO_MERGE = [
    "test_dataset_l.jsonl",
    "test_dataset_u.jsonl",
    "test_dataset_w.jsonl"
]

INPUT_FOLDER = "jsonl_files"
OUTPUT_FOLDER = "jsonl_merged_files"
MODEL_NAME = "dataset"

def safe_json_load(line):
    """Attempts to fix common JSON formatting issues."""
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

def merge_manual_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_folder = os.path.join(base_dir, INPUT_FOLDER)
    out_folder = os.path.join(base_dir, OUTPUT_FOLDER)
    os.makedirs(out_folder, exist_ok=True)

    all_available = glob.glob(os.path.join(root_folder, "**", "*.jsonl"), recursive=True)
    files_map = {os.path.basename(f): f for f in all_available}

    final_files_to_process = []
    missing_files = []
    for name in FILES_TO_MERGE:
        if name in files_map:
            final_files_to_process.append(files_map[name])
        else:
            missing_files.append(name)

    if missing_files:
        print("\n⚠ The following files were NOT found:")
        for mf in missing_files:
            print(f" - {mf}")
    
    if not final_files_to_process:
        print("\n❌ No files found for processing. Check FILES_TO_MERGE.")
        return

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_path = os.path.join(out_folder, f"{MODEL_NAME}_{timestamp}_merged.jsonl")

    print(f"\n🚀 Starting merge into: {output_path}")
    
    stats = {"total": 0, "repaired": 0, "written": 0}
    total_size = sum(os.path.getsize(f) for f in final_files_to_process)
    is_first_record = True

    with open(output_path, 'w', encoding='utf-8') as outfile, \
         tqdm(total=total_size, unit='B', unit_scale=True, desc="Progress") as pbar:
        
        for file_path in final_files_to_process:
            with open(file_path, 'r', encoding='utf-8') as infile:
                for line in infile:
                    raw = line.strip()
                    if not raw:
                        pbar.update(len(line.encode('utf-8')))
                        continue
                    
                    stats["total"] += 1
                    try:
                        data = json.loads(raw)
                    except:
                        data = safe_json_load(raw)
                        if data:
                            stats["repaired"] += 1
                        else:
                            data = {}

                    record = ift_record(data)

                    if any(record.values()):
                        json_str = json.dumps(record, ensure_ascii=False)
                        
                        if is_first_record:
                            outfile.write(json_str)
                            is_first_record = False
                        else:
                            outfile.write("\n" + json_str)
                        
                        stats["written"] += 1
                    
                    pbar.update(len(line.encode('utf-8')))

    print("\n" + "="*40)
    print(f"📊 TOTAL FILES PROCESSED: {len(final_files_to_process)}")
    print(f"📄 Lines read: {stats['total']}")
    print(f"🛠 Repaired JSON objects: {stats['repaired']}")
    print(f"✅ Records written: {stats['written']}")
    print("="*40)

if __name__ == "__main__":
    merge_manual_files()
