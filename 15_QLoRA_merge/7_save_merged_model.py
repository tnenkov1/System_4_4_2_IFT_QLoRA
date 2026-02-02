# Save merged model and tokenizer
os.makedirs(output_path, exist_ok=True)

print("Saving merged model...")
merged.save_pretrained(output_path, safe_serialization=True)

print("Saving tokenizer...")
tokenizer.save_pretrained(output_path)