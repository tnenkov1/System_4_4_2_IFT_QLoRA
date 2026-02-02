# Tokenizer
print("Loading tokenizer and fixing EOS token...")
tokenizer = AutoTokenizer.from_pretrained(base_model_path, use_fast=True)

# For stable text generation stopping
if tokenizer.eos_token is None:
    tokenizer.eos_token = "<|endoftext|>"

tokenizer.pad_token = tokenizer.eos_token