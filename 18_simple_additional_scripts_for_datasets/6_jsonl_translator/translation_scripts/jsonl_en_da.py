import os
import json
import requests
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from time import sleep
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "jsonl_files")
OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "translated_jsonl_files")
LOG_DIR = os.path.join(BASE_DIR, "logs")

PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
PROMPT_FILE = os.path.join(PROMPTS_DIR, "translate_en_da.txt")

MODEL = ""
API_URL = "http://localhost:11434/api/generate"

MAX_WORKERS = 2
SLEEP_BETWEEN_REQUESTS = 0.05
MAX_CHUNK_WORDS = 400
MAX_RETRIES = 3

TARGET_FIELDS = ("prompt", "completion", "instruction", "input", "output", "text")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)

RUN_TS = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, RUN_TS)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================== LOGGING ==================
log_file = os.path.join(LOG_DIR, f"run_{RUN_TS}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================== LOAD PROMPT ==================
def load_prompt_template():
    if not os.path.exists(PROMPT_FILE):
        raise FileNotFoundError(
            f"❌ Липсва prompt файл: {PROMPT_FILE}\n"
            f"➡️ Създай го и постави prompt-а вътре."
        )
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_TEMPLATE = load_prompt_template()

# ================== SESSION ==================
session = requests.Session()

# ================== CHUNK ==================
def split_text_into_chunks(text: str, max_words: int = MAX_CHUNK_WORDS):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        if len((current_chunk + " " + p).split()) > max_words:
            if current_chunk:
                chunks.append(current_chunk.strip())

            if len(p.split()) > max_words:
                sentences = re.split(r'(?<=[.!?])\s+', p)
                temp_chunk = ""
                for s in sentences:
                    if len((temp_chunk + " " + s).split()) > max_words:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                        temp_chunk = s
                    else:
                        temp_chunk += " " + s
                if temp_chunk:
                    chunks.append(temp_chunk.strip())
                current_chunk = ""
            else:
                current_chunk = p
        else:
            current_chunk += " " + p

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# ================== TRANSLATION ==================
def translate_chunk(text: str) -> str:
    prompt = PROMPT_TEMPLATE.replace("{TEXT}", text)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with session.post(
                API_URL,
                json={"model": MODEL, "prompt": prompt},
                stream=True,
                timeout=180
            ) as r:
                r.raise_for_status()
                result = ""
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line.decode("utf-8"))
                        result += data.get("response", "")
                    except json.JSONDecodeError:
                        continue

                if result.strip():
                    return result.strip()

        except Exception as e:
            logger.warning(f"Грешка при превод (опит {attempt}/{MAX_RETRIES}): {e}")
            sleep(1)

    logger.error("Максимален брой опити достигнат. Връщам оригиналния текст.")
    return text

# ================== JSONL FILE ==================
def translate_jsonl_file(path: str):
    with open(path, "r", encoding="utf-8") as f_in:
        entries = [json.loads(line) for line in f_in]

    out_path = os.path.join(
        OUTPUT_DIR,
        os.path.splitext(os.path.basename(path))[0] + "_da.jsonl"
    )

    with open(out_path, "w", encoding="utf-8") as f_out:
        for entry in tqdm(entries, desc=os.path.basename(path), unit="entry", leave=False):
            for field in TARGET_FIELDS:
                text = entry.get(field)
                if isinstance(text, str) and text.strip():
                    chunks = split_text_into_chunks(text)
                    translated_chunks = [""] * len(chunks)

                    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                        future_to_idx = {
                            executor.submit(translate_chunk, chunk): i
                            for i, chunk in enumerate(chunks)
                        }
                        for future in as_completed(future_to_idx):
                            idx = future_to_idx[future]
                            try:
                                translated_chunks[idx] = future.result()
                            except Exception:
                                translated_chunks[idx] = chunks[idx]
                            sleep(SLEEP_BETWEEN_REQUESTS)

                    entry[field] = "\n\n".join(translated_chunks)

            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f_out.flush()

    logger.info(f"Преведен файл: {os.path.basename(out_path)}")

# ================== BATCH ==================
def batch_translate():
    logger.info(f"Избран модел: {MODEL}")
    logger.info("=== START TRANSLATION RUN ===")

    try:
        r = session.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code != 200:
            raise Exception("Ollama API не е достъпен")
    except Exception as e:
        logger.error(e)
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".jsonl")]

    if not files:
        logger.warning("Няма .jsonl файлове за превод")
        logger.info("=== END TRANSLATION RUN ===")
        return

    for fname in files:
        translate_jsonl_file(os.path.join(INPUT_DIR, fname))

    logger.info(f"ЗАВЪРШЕНО | Output: {OUTPUT_DIR}")
    logger.info("=== END TRANSLATION RUN ===")

# ================== MAIN ==================
if __name__ == "__main__":
    batch_translate()
