from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import os
import shutil

# Base directory (directory from which the script is executed)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

base_model_path = os.path.join(BASE_DIR, "LLM")
lora_path = os.path.join(BASE_DIR, "LoRA")
output_path = os.path.join(BASE_DIR, "FineTunedModel")

print("Base directory:", BASE_DIR)

# Load base model
print("Loading base model...")
base = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    device_map="cpu"
)

# Tokenizer
print("Loading tokenizer and fixing EOS token...")
tokenizer = AutoTokenizer.from_pretrained(base_model_path, use_fast=True)

# For stable text generation stopping
if tokenizer.eos_token is None:
    tokenizer.eos_token = "<|endoftext|>"

tokenizer.pad_token = tokenizer.eos_token

# Load LoRA adapter
print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(base, lora_path)

# Merging the LoRA adapters with the base model
print("Merging LoRA with base model...")
merged = model.merge_and_unload()

merged.config.pad_token_id = tokenizer.pad_token_id
merged.config.eos_token_id = tokenizer.eos_token_id

# Save merged model and tokenizer
os.makedirs(output_path, exist_ok=True)

print("Saving merged model...")
merged.save_pretrained(output_path, safe_serialization=True)

print("Saving tokenizer...")
tokenizer.save_pretrained(output_path)

# Copy special tokenizer files if they exist
for file in ["special_tokens_map.json", "tokenizer_config.json"]:
    src = os.path.join(lora_path, file)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(output_path, file))

print("DONE! The merged model is ready at:", output_path)
