#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 1. Preparation for instruction fine-tuning

import os, json, torch, gc
from torch.utils.data import Dataset, SequentialSampler
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, Trainer, 
    TrainingArguments, DataCollatorForLanguageModeling, BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

def clear_mem():
    gc.collect()
    torch.cuda.empty_cache()

clear_mem() # Clears VRAM before you start
print(f"✅ GPU: {torch.cuda.get_device_name(0)}")


# In[ ]:


# 2. Configuration for instruction fine-tuning

MODEL_PATH = "/workspace/work/LLM" # Path for the base language model for fine-tuning (contains all the .safetensors files, tokenizers, configs and etc.)
DATASET_PATH = "/workspace/work/datasets/dataset1.jsonl" # Path for the dataset for fine-tuning
OUTPUT_DIR = "/workspace/work/outputs/Gemma_2_System_4_4_2" # Path for the checkpoints created during fine-tuning and for the LoRA adapters at the end.

MAX_LENGTH = 1024 # The number of tokens (~800 words per example from the dataset). If there are bigger examples than that, the model will not learn the whole example. 
# Increasing max_length, leads to more VRAM usage and vice versa. You can set max_length lower than your dataset example length, only if you add chunkning logic, but here that's not the case.

BATCH_SIZE = 1 # The number of examples, the language model looks at, at the same time.
GRAD_ACC = 16  # The number of batches, the language model adds up before updating its weights.
# Batch_size * grad_acc = training step (the number of examples the language model see, before updating its weights)
# Increasing batch_size, leads to more VRAM usage and vice versa.
# Increasing gradient_accumulation, leads to the increase of the training time.
# If you haven't got enough VRAM, you can compensate with increasing the time for fine-tuning (in case you need to make the model see more examples at once).
# In this case, 1 training step will be 16 examples.

EPOCHS = 2 # The number of times, the language model runs through the examples from the dataset.
# Repetition is mother of knowledge when it occurs during learning (in the dataset) and father of dulling when it occurs during comprehension/understanding (with more epochs of fine-tuning).

LR = 5e-5  # Learning Rate is the size of the step, the language model make before updating its weights. (in this case, 5e-5 is scientific notation for the number 0.00005)
# Bigger steps for fast, but unstable learning.
# Smaller steps for slow, but relatively stable learning.

LORA_R = 128   # rank of the Low-Rank Adaptation (LoRA rank).
# Increasing lora_r, leads to more VRAM usage and vice versa. When you increase lora_r, you increase the number of parameters that will be fine-tuned. 
# During fine-tuning, I noticed that when you increase lora_r, you make the language model think more analytically.
# So increasing of lora_r makes the language model sharper, while decreasing the lora_r makes the model less adaptive.

LORA_ALPHA = 4 # scaling factor for the LoRA update.
# Changing lora_alpha, leads to changing the influence, that the dataset cause to the parameters that will be fine-tuned 
# During fine-tuning, I noticed that when you decrease lora_alpha, you make the language model think more critically.
# So increasing of lora_alpha makes the language model more naive(trusts easy to the new data from the dataset), while decreasing the lora_alpha makes the model more aware (trusts hard and needs time).
# Lora_r is like "worldview" (мироглед) - The bigger it is, the bigger is the capacity for learning. 
# Lora_alpha is like "trust" (доверие) - The smaller it is, the bigger is the understanding.

LORA_DROPOUT = 0.05 # This causes the language model to ignore 5 % of the trained parameters, which leads to not becoming so attached to the new information in the dataset. 
# This is the humility (смирението) of the language model. The bigger it is, the better it learns.
# The bigger the worldview and the humility and the smaller the trust, leads to fine-tuning better language models.


# In[ ]:


# 3. Checking if there are language model and dataset in the paths
def check_paths():
    m_ok = os.path.exists(MODEL_PATH)
    d_ok = os.path.exists(DATASET_PATH)
    print(f"Base model: {'✅' if m_ok else '❌'}")
    print(f"Dataset: {'✅' if d_ok else '❌'}")
    if not (m_ok and d_ok):
        raise FileNotFoundError("Error: Check paths!")

check_paths()


# In[ ]:


# 4. QLoRA configuration and loading the language model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    low_cpu_mem_usage=True  
)

# Активиране на икономията на памет
model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=LORA_R, 
    lora_alpha=LORA_ALPHA,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()


# In[ ]:


# 5. Phases during fine-tuning
# The language model goes through the "learn" examples first, then the "understand" examples, and finally the "work" examples.

class CognitiveSequentialDataset(Dataset):
    def __init__(self, path, tokenizer, max_length):
        self.tokenizer = tokenizer
        self.max_length = max_length
        with open(path, "r", encoding="utf-8") as f:
            self.examples = [json.loads(line) for line in f if line.strip()]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        phase = ex.get("phase", "work")
        instr = ex.get("instruction", "").strip()
        inp = ex.get("input", "").strip()
        out = ex.get("output", "").strip()

        prompt_part = f"### Instruction:\n{instr}\n\n### Input:\n{inp}\n\n### Response:\n"
        full_text = prompt_part + out + self.tokenizer.eos_token

        enc = self.tokenizer(full_text, truncation=True, max_length=self.max_length, padding=False)
        input_ids = list(enc["input_ids"])
        labels = list(input_ids)

        if phase != "learn":
            prompt_enc = self.tokenizer(prompt_part, add_special_tokens=False, truncation=True, max_length=self.max_length)
            prompt_len = len(prompt_enc["input_ids"])
            for i in range(min(prompt_len, len(labels))):
                labels[i] = -100 # The model does not learn from this tokens.

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(enc["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long)
        }

train_dataset = CognitiveSequentialDataset(DATASET_PATH, tokenizer, MAX_LENGTH)


# In[ ]:


# 6. Giving the examples from the dataset sequentially to the language model (shuffle=False)
class StrictSequentialTrainer(Trainer):
    def _get_train_sampler(self, dataset):
        return SequentialSampler(dataset)


# In[ ]:


# 7. Final settings
SAVE_STEPS = 250        # Saves checkpoint for the fine-tuning on every 250 training steps. (250 * 16 = 4000 examples)
SAVE_TOTAL_LIMIT = 2    # Stores only the last two checkpoint files to save disk space. (The bigger the lora_r, the bigger the checkpoints and adapters get).

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACC,
    learning_rate=LR,
    num_train_epochs=EPOCHS,

    # Optimizations
    fp16=True, # Makes the language model use two times less VRAM during calculations. Faster fine-tuning.
    optim="paged_adamw_8bit", # Optimizer for the weight updates
    weight_decay=0.1,       # Help against overtraining (overfitting)

    # Logging (отчет)
    logging_steps=10,       # Fine-tuning progress bar updates on every 10 training steps (10 steps * 16 examples = 160 examples)
    report_to="none",

    # Saving checkpoints using steps
    save_strategy="steps",          
    save_steps=SAVE_STEPS,         
    save_total_limit=SAVE_TOTAL_LIMIT,

    # Saving memory and stabilizating the fine-tuning
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False},

    # Optional for Windows
    dataloader_pin_memory=True,   # Load examples in a reserved space in the RAM to get them ready for the GPU when needed. Reducing the time, the GPU stays empty while waiting the CPU to transfer the training examples.
    dataloader_num_workers=0      # Number of parallel loading processes. In this case is only the main one.
)

trainer = StrictSequentialTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

clear_mem()
print(f" Starting System 4-4-2 Instruction Fine-Tuning (в {OUTPUT_DIR})...")


# In[ ]:


# 8. Beginning of the language model fine-tuning
print("Starting Fine-Tuning (Learn -> Understand -> Work)")
trainer.train()


# In[ ]:


# 9. Ending of the language model fine-tuning
final_path = os.path.join(OUTPUT_DIR, "cognitive_final_model")  # Saves the LoRA adapters into the output folder
trainer.save_model(final_path) 
tokenizer.save_pretrained(final_path)
print(f"End! The LoRA adapters of the language model are saved in: {final_path}")

