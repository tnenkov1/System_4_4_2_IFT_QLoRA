MODEL = "todorov/bggpt:9B-IT-v1.0.Q6_K" # The language model for translation can be changed by replacing this name with another model name from (cmd "ollama list")
API_URL = "http://localhost:11434/api/generate" #BgGPT - INSAIT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "docx_files")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "translated_docx_files")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PROMPTS_JSON = os.path.join(PROMPTS_DIR, "prompt_list.json")

for folder in [INPUT_DIR, PROMPTS_DIR, OUTPUT_BASE_DIR, LOGS_DIR]:
    os.makedirs(folder, exist_ok=True)

RUN_TS = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOGS_DIR, f"log_{RUN_TS}.txt")
SESSION_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, RUN_TS)

def write_log(message):
    """Writes a log entry with timestamp."""
    now = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")

def get_lang_suffix(prompt_filename):
    """
    Extracts the language suffix from filename.
    Example: 'translate_en.txt' -> 'en'
    """
    name_part = prompt_filename.replace(".txt", "")
    parts = name_part.split("_")
    return parts[-1] if len(parts) > 1 else "tr"