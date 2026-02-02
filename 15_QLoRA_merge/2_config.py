# Base directory (directory from which the script is executed)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

base_model_path = os.path.join(BASE_DIR, "LLM")
lora_path = os.path.join(BASE_DIR, "LoRA")
output_path = os.path.join(BASE_DIR, "FineTunedModel")

print("Base directory:", BASE_DIR)