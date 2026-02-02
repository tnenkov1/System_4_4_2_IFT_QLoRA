# Load base model
print("Loading base model...")
base = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    device_map="cpu"
)
