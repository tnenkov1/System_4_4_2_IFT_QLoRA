import os
import re
import json
import requests
import time
from datetime import datetime
from docx import Document
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# ================== CONFIG ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "docx_files")
OUTPUT_DIR = os.path.join(BASE_DIR, "jsonl_files")

RUN_TS = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RUN_DIR = os.path.join(OUTPUT_DIR, RUN_TS)

API_URL = "http://127.0.0.1:11434/api/generate"
TAGS_URL = "http://127.0.0.1:11434/api/tags"

MAX_WORKERS = 1  
TIMEOUT = 180 

# ================== SETUP ==================
for d in [INPUT_DIR, RUN_DIR]:
    os.makedirs(d, exist_ok=True)

# ================== OLLAMA MODELS ==================
def get_models():
    try:
        r = requests.get(TAGS_URL, timeout=5)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        return []

# ================== TEXT HELPERS ==================
def extract_words(path):
    try:
        doc = Document(path)
        text = " ".join(p.text for p in doc.paragraphs)
        words = re.findall(r"[А-Яа-яA-Za-z]+", text)
        clean = set()
        for w in words:
            wl = w.lower()
            if len(wl) > 3: 
                clean.add(wl)
        return clean
    except Exception as e:
        print(f"❌ Error reading file {path}: {e}")
        return set()

def word_root(word, n=6):
    return word[:n] if len(word) >= n else word

def clean_llm_output(text):
    if not text:
        return ""
    text = re.sub(r'^[^\n:]+[:\n]', '', text).strip()
    text = text.replace("\n", ",")
    parts = [p.strip().lower() for p in text.split(",") if p.strip()]
    return ", ".join(list(dict.fromkeys(parts)))

def get_prompt(group_words):
    return (
        "### System: You are a precise data formatting tool.\n"
        "### Task:\n"
        "Analyze the following cluster of structurally related words:\n"
        f"[{group_words}]\n\n"
        "Generate between 5 and 10 distinct, semantically connected words or associations based on them.\n\n"
        "### Output Constraints:\n"
        "- Return ONLY the final list of words, separated by commas.\n"
        "- Do NOT include introductory text, numbering, bullet points, markdown formatting, or explanations.\n"
        "- Match the language of the provided input words.\n"
        "### Output:"
    )

# ================== OLLAMA CALL ==================
def call_ollama(model, group_input, session):
    payload = {
        "model": model,
        "prompt": get_prompt(group_input),
        "stream": False,
        "options": {
            "temperature": 0.6,
            "num_predict": 1024
        }
    }
    for _ in range(2):
        try:
            r = session.post(API_URL, json=payload, timeout=TIMEOUT)
            if r.status_code == 200:
                return clean_llm_output(r.json().get("response", ""))
            else:
                time.sleep(1)
        except Exception:
            time.sleep(2)
    return None

def get_processed_inputs(jsonl_path):
    done = set()
    if not os.path.exists(jsonl_path):
        return done
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    done.add(data.get("input", ""))
                except:
                    pass
    except:
        pass
    return done

# ================== MAIN ==================
def main():
    print(f"🚀 Starting execution session: {RUN_TS}")
    
    # Model Selection Strategy
    models = get_models()
    if not models:
        print("❌ No models available in Ollama or service is offline.")
        return

    print("\n--- Available Models ---")
    for i, m in enumerate(models, 1):
        print(f"{i}. {m}")

    try:
        choice = int(input("\nSelect a model number: ")) - 1
        model = models[choice]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    # 1. Word Extraction
    all_words = set()
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".docx")]
    
    if not files:
        print(f"⚠️ No files discovered in directory: {INPUT_DIR}")
        return

    print(f"📂 Reading data from {len(files)} document(s)...")
    for f in tqdm(files, desc="Reading DOCX files"):
        all_words.update(extract_words(os.path.join(INPUT_DIR, f)))

    if not all_words:
        print("⚠️ No valid words extracted.")
        return

    # --- Write extracted words directly to a TXT file ---
    sorted_words = sorted(list(all_words))
    txt_path = os.path.join(RUN_DIR, f"extracted_words_{RUN_TS}.txt")
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted_words))
        print(f"📄 Generated wordlist detailing {len(sorted_words)} elements exported to: {txt_path}")
    except Exception as e:
        print(f"❌ Error compiling output TXT document: {e}")

    # 2. Word Grouping
    groups = defaultdict(list)
    for w in sorted_words:
        groups[word_root(w)].append(w)
    
    print(f"✅ Parsed words aggregated into {len(groups)} distinct lexical clusters.")

    # 3. Knowledge Graph Generation
    jsonl_path = os.path.join(RUN_DIR, f"knowledge_graph_{RUN_TS}.jsonl")
    processed = get_processed_inputs(jsonl_path)
    session = requests.Session()

    print(f"🧠 Initializing inference generation with Ollama engine using model: {model}...")

    with open(jsonl_path, "a", encoding="utf-8") as out:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futures = {}
            
            for root, forms in groups.items():
                group_input = ", ".join(forms)
                if group_input not in processed:
                    futures[ex.submit(call_ollama, model, group_input, session)] = group_input

            for fut in tqdm(as_completed(futures), total=len(futures), desc="Ollama Inference"):
                group_input = futures[fut]
                associations = fut.result()

                if associations and len(associations.split(",")) >= 3:
                    entry1 = {"instruction": "", "input": group_input, "output": associations}
                    entry2 = {"instruction": "", "input": associations, "output": group_input}

                    out.write(json.dumps(entry1, ensure_ascii=False) + "\n")
                    out.write(json.dumps(entry2, ensure_ascii=False) + "\n")
                    out.flush()

    print(f"✅ Process finalized successfully!")
    print(f"📁 Session artifacts saved in folder location: {RUN_DIR}")

if __name__ == "__main__":
    main()