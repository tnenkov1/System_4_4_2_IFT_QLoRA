import datetime
import json
import os
import re
import sys
import requests
from tqdm import tqdm

# ================== CONFIGURATION ==================
INPUT_DIR = "jsonl_files"
OUTPUT_BASE_DIR = "translated_jsonl_files"

SCRIPTS_DIR = "translation_scripts"
SCRIPTS_LIST_FILE = os.path.join(SCRIPTS_DIR, "scripts_list.json")
PROMPTS_DIR = "prompts"  # Folder containing custom text prompts

API_URL = "http://localhost:11434/api/generate"
TAGS_URL = "http://localhost:11434/api/tags"

# Setup output folders
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)
RUN_TS = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, RUN_TS)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== OLLAMA MODELS ==================
def get_models():
    """Fetches all currently available models from the local Ollama instance."""
    try:
        r = requests.get(TAGS_URL, timeout=5)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        return []

# ================== TRANSLATION CORE ==================
def get_custom_prompt(lang_item, text):
    """Loads a custom prompt from a .txt file and safely maps variables case-insensitively."""
    prompt_filename = lang_item["name"].replace("docx_", "translate_").replace("jsonl_", "translate_").replace(".py", ".txt")
    prompt_path = os.path.join(PROMPTS_DIR, prompt_filename)

    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            lowered_template = template.lower()
            if "{lang_desc}" in lowered_template and ("{text}" in lowered_template or "{text}" in template.lower()):
                standardized = re.sub(r'(?i)\{text\}', '{text}', template)
                standardized = re.sub(r'(?i)\{lang_desc\}', '{lang_desc}', standardized)
                return standardized.format(lang_desc=lang_item["desc"], text=text)
            else:
                return f"{template.strip()}\n\nTARGET LANGUAGE:\n{lang_item['desc']}\n\nTEXT:\n{text}\n\nTRANSLATION:\n"
        except Exception as e:
            print(f"⚠️ Error reading custom prompt file {prompt_filename}: {e}")

    # Fallback template
    return f"""Instruction: Act as a precise translation engine. Translate the text below into {lang_item['desc']}. 
Strict Rules: Output ONLY the raw translation. Do not include notes, introductions, markdown formatting, quotes, or explanations.

TEXT:
{text}

TRANSLATION:"""

def clean_llm_response(response, original_text):
    """Aggressively strips formatting markers, conversational bloat, and prompt leaks."""
    if not response:
        return original_text

    response = response.strip()

    if "TRANSLATION:" in response:
        parts = response.split("TRANSLATION:")
        response = parts[-1].strip()

    response = re.sub(r"(?i).*english\s*(->|→)\s*[a-zа-я\s]+.*", "", response)
    response = re.sub(r"(?i).*[a-zа-я]+\s*(->|→)\s*[a-zа-я\s]+.*", "", response)

    prompt_leak_patterns = [
        r"(?i)task:",
        r"(?i)target language:",
        r"(?i)strict rules:",
        r"(?i)text to translate:",
        r"(?i)text:",
        r"(?i)result:",
    ]
    for pattern in prompt_leak_patterns:
        response = re.sub(pattern, "", response)

    prefixes_to_remove = [
        "here is the translation:",
        "translation:",
        "translated text:",
        "tuk e prevodat:",
        "prevod:",
        "french:",
        "english:",
    ]
    for prefix in prefixes_to_remove:
        if response.lower().startswith(prefix):
            response = response[len(prefix) :].strip()

    lines = [line.strip() for line in response.splitlines() if line.strip()]
    response = "\n".join(lines).strip()

    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1].strip()
    if response.startswith("'") and response.endswith("'"):
        response = response[1:-1].strip()

    return response if response else original_text

def translate_text(text, lang_item, model, session):
    if not text or not str(text).strip() or len(str(text).strip()) < 2:
        return text

    prompt = get_custom_prompt(lang_item, str(text))

    try:
        r = session.post(
            API_URL,
            json={
                "model": model, 
                "prompt": prompt, 
                "stream": False,
                "system": "You are a literal, word-for-word document translation API. You never converse, you never explain, and you never use markdown blocks. You only output pure text translations.",
                "options": {
                    "temperature": 0.5,
                    "top_p": 0.1
                }
            },
            timeout=180,
        )
        r.raise_for_status() 
        
        resp_data = r.json()
        if "error" in resp_data:
            tqdm.write(f"❌ Ollama API Error: {resp_data['error']}")
            return text

        raw_response = resp_data.get("response", "").strip()
        if not raw_response:
            return text

        return clean_llm_response(raw_response, str(text))
    except Exception as e:
        tqdm.write(f"⚠️ Translation failed for text block. Error: {e}")
        return text

def run_jsonl_translation(file_name, lang_item, model, session):
    file_path = os.path.join(INPUT_DIR, file_name)
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    lang_folder = os.path.join(OUTPUT_DIR, lang_item["name"].replace(".py", ""))
    os.makedirs(lang_folder, exist_ok=True)
    output_path = os.path.join(lang_folder, file_name)

    KNOWN_FIELDS = {"text", "prompt", "completion", "instruction", "input", "output", "content"}

    with open(output_path, "w", encoding="utf-8") as out_f:
        for line in tqdm(lines, desc=f"    ↳ File: {file_name[:20]}", unit="line", colour="green", leave=True):
            if not line.strip():
                out_f.write("\n")
                continue
            
            try:
                data = json.loads(line)
                
                found_keys = [k for k in KNOWN_FIELDS if k in data and isinstance(data[k], str)]
                
                if found_keys:
                    for key in found_keys:
                        if data[key].strip():
                            data[key] = translate_text(data[key], lang_item, model, session)
                else:
                    for key, value in data.items():
                        if isinstance(value, str) and len(value.strip()) > 1:
                            data[key] = translate_text(value, lang_item, model, session)
                            
                out_f.write(json.dumps(data, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                translated_line = translate_text(line.strip(), lang_item, model, session)
                out_f.write(translated_line + "\n")

# ================== MAIN INTERFACE ==================
def main():
    models = get_models()
    if not models:
        print("❌ No models available in Ollama or service is offline.")
        return

    print("\n=== SELECT OLLAMA MODEL ===")
    for i, m in enumerate(models, 1):
        print(f"{i:2}. {m}")

    try:
        model_choice = int(input("\nSelect a model number: ")) - 1
        chosen_model = models[model_choice]
    except (ValueError, IndexError):
        print("❌ Invalid model choice.")
        return

    if not os.path.exists(SCRIPTS_LIST_FILE):
        print(f"❌ Error: Missing configuration file at {SCRIPTS_LIST_FILE}")
        return
        
    with open(SCRIPTS_LIST_FILE, "r", encoding="utf-8") as f:
        languages = json.load(f)

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".jsonl")]
    if not files:
        print(f"⚠️ No JSONL documents discovered in folder directory '{INPUT_DIR}'")
        return

    print(f"\n✅ Found {len(files)} file(s) ready for translation processing.")
    print("=== SELECT TARGET LANGUAGES ===")
    for idx, lang in enumerate(languages, 1):
        print(f"{idx:2}. {lang['desc']}")

    selection = (
        input("\nEnter language numbers separated by commas (e.g., 1,3,5) or 'all': ")
        .strip()
        .lower()
    )

    if selection == "all":
        chosen_langs = languages
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            chosen_langs = [languages[i] for i in indices if 0 <= i < len(languages)]
        except:
            print("❌ Invalid language selection choice.")
            return

    if not chosen_langs:
        print("⚠️ No valid languages selected.")
        return

    session = requests.Session()
    print(f"\n🚀 Launching translation pipeline targeting {len(files)} file(s) across {len(chosen_langs)} language profile(s) using model '{chosen_model}'...\n")

    for idx, lang in enumerate(chosen_langs, 1):
        print(f"\n[ Language Profile {idx}/{len(chosen_langs)} ] Active target: {lang['desc']}")
        for file_name in files:
            run_jsonl_translation(file_name, lang, chosen_model, session)

    print(f"\n✨ Process completed successfully! Output saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()