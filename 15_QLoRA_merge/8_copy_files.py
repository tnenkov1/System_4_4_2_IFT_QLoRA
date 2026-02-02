# Copy special tokenizer files if they exist
for file in ["special_tokens_map.json", "tokenizer_config.json"]:
    src = os.path.join(lora_path, file)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(output_path, file))

print("DONE! The merged model is ready at:", output_path)