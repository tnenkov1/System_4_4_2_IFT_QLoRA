import os
import shutil
import argparse
from tqdm import tqdm

# ================== CLI ARGUMENTS ==================
parser = argparse.ArgumentParser(description="Collect and process JSONL files")
parser.add_argument("--dry-run", action="store_true", help="Show files to be processed without copying")
parser.add_argument("--no-prefix", action="store_true", help="Do not add subfolder prefix to the filename")
parser.add_argument("--merge", action="store_true", help="Merge all discovered files into a single master file")
args = parser.parse_args()

# ================== DIRECTORIES CONFIGURATION ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_DIR = os.path.join(BASE_DIR, "translated_jsonl_files")
DEST_DIR = os.path.join(BASE_DIR, "translated_files_sum")

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

# ================== FILE DISCOVERY ==================
jsonl_files = []
for root, _, files in os.walk(SOURCE_DIR):
    for file in files:
        if file.lower().endswith(".jsonl"):
            jsonl_files.append(os.path.join(root, file))

if not jsonl_files:
    print(f"⚠️ No .jsonl files discovered in target folder:\n{SOURCE_DIR}")
    exit(0)

print(f"✅ Discovered files: {len(jsonl_files)}")

# ================== INITIALIZE MERGE MODE ==================
total_lines = 0
merged_path = os.path.join(DEST_DIR, "merged.jsonl")

if args.merge and not args.dry_run:
    merged_file = open(merged_path, "w", encoding="utf-8")

copied_count = 0

# ================== FILE PROCESSING LOOP ==================
for src in tqdm(jsonl_files, desc="Processing files", unit="file"):
    folder_name = os.path.basename(os.path.dirname(src))
    file_name = os.path.basename(src)

    if not args.no_prefix:
        file_name = f"{folder_name}__{file_name}"

    dest_path = os.path.join(DEST_DIR, file_name)

    # Overwrite protection / Collision handling
    base, ext = os.path.splitext(dest_path)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = f"{base}_{counter}{ext}"
        counter += 1

    # Read lines and count records
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()
        total_lines += len(lines)

        if args.merge and not args.dry_run:
            merged_file.writelines(lines)

    if args.dry_run:
        print(f"[DRY-RUN] Would process: {src}")
        continue

    shutil.copy2(src, dest_path)
    copied_count += 1

if args.merge and not args.dry_run:
    merged_file.close()

# ================== EXECUTION REPORT ==================
print("\n📊 EXECUTION REPORT")
print(f"✔ Files Discovered : {len(jsonl_files)}")
print(f"✔ Files Copied     : {copied_count}")
print(f"✔ Total Lines/Rows : {total_lines}")
print(f"📁 Output Directory: {DEST_DIR}")

if args.merge and not args.dry_run:
    print(f"📄 Merged Master   : {merged_path}")

print("\n✨ Process completed successfully!")