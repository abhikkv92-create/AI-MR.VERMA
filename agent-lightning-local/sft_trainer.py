"""
Supervised Fine-Tuning Trainer
──────────────────────────────
Uses Unsloth + LoRA to fine-tune Qwen 2.5 Coder 7B on high-reward examples.
Designed for 16GB RAM with gradient checkpointing.
After RAM upgrade to 32GB: increase batch_size to 4, max_seq_length to 8192.

PREREQUISITES:
  - 500+ accumulated SFT examples in /app/data/sft_batches/
  - Run this manually: docker exec -it agl-trainer python sft_trainer.py
"""

import os
import glob
import json
import logging

log = logging.getLogger(__name__)
SFT_DIR = "/app/data/sft_batches"
CHECKPOINT_DIR = "/app/checkpoints"


def prepare_dataset():
    """Combine all SFT batches into a single training dataset."""
    all_examples = []
    for filepath in sorted(glob.glob(os.path.join(SFT_DIR, "sft_batch_*.json"))):
        with open(filepath) as f:
            data = json.load(f)
            all_examples.extend(data)

    log.info(f"Total SFT examples: {len(all_examples)}")

    # Sort by reward — use the best examples
    all_examples.sort(key=lambda x: x.get("reward", 0), reverse=True)

    # Format for training
    formatted = []
    for ex in all_examples:
        formatted.append({
            "text": (
                f"### Instruction:\n{ex['instruction']}\n\n"
                f"### Response:\n{ex['output']}"
            )
        })

    combined_path = os.path.join(SFT_DIR, "combined_sft.json")
    with open(combined_path, "w") as f:
        json.dump(formatted, f)

    log.info(f"Combined dataset saved: {combined_path}")
    return combined_path


def train():
    """Run LoRA fine-tuning with Transformers + PEFT (CPU Optimized)."""
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import load_dataset

    dataset_path = prepare_dataset()

    # Load Dynamic Parameters
    config_path = "/app/config/sft_params.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            sft_config = json.load(f)
        log.info(f"Loaded autonomous SFT config: {sft_config}")
    else:
        sft_config = {
            "learning_rate": 2e-4,
            "per_device_train_batch_size": 1,
            "gradient_accumulation_steps": 4,
            "max_steps": 10,
            "lora_r": 8,
            "lora_alpha": 32,
            "target_model": "Qwen/Qwen2.5-Coder-1.5B-Instruct"
        }

    # Load Tokenizer (Always use the base size for consistency)
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct")
    tokenizer.pad_token = tokenizer.eos_token

    TRAINING_MODEL_ID = sft_config.get("target_model", "Qwen/Qwen2.5-Coder-1.5B-Instruct")
    
    log.info(f"Loading {TRAINING_MODEL_ID} for CPU Fine-Tuning...")
    model = AutoModelForCausalLM.from_pretrained(
        TRAINING_MODEL_ID,
        torch_dtype=torch.float32, # CPU standard
        device_map="cpu",
    )

    # Configure LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=sft_config.get("lora_r", 8),
        lora_alpha=sft_config.get("lora_alpha", 32),
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Load Dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    log.info(f"Training on {len(dataset)} examples...")
    
    trainer = Trainer(
        model=model,
        train_dataset=tokenized_datasets,
        args=TrainingArguments(
            output_dir=os.path.join(CHECKPOINT_DIR, "sft_output"),
            per_device_train_batch_size=sft_config.get("per_device_train_batch_size", 1),
            gradient_accumulation_steps=sft_config.get("gradient_accumulation_steps", 4),
            max_steps=sft_config.get("max_steps", 10),
            learning_rate=sft_config.get("learning_rate", 2e-4),
            use_cpu=True, # Explicitly use CPU
            logging_steps=1,
            save_steps=5,
        ),
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    trainer.train()

    # Save Adapter
    adapter_dir = os.path.join(CHECKPOINT_DIR, "adapter_output")
    model.save_pretrained(adapter_dir) 
    log.info(f"Adapter saved to: {adapter_dir}")
    
    log.info("=" * 60)
    log.info("SFT COMPLETE (CPU MODE)")
    log.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train()
