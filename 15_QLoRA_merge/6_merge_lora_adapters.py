# Merging the LoRA adapters with the base model
print("Merging LoRA with base model...")
merged = model.merge_and_unload()

merged.config.pad_token_id = tokenizer.pad_token_id
merged.config.eos_token_id = tokenizer.eos_token_id