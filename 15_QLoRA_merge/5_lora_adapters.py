# Load LoRA adapter
print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(base, lora_path)