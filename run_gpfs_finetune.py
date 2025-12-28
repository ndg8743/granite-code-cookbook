"""
Fine-tune Granite model on IBM Storage Scale (GPFS) dataset.
Uses PyTorch 2.9.1+cu128 for RTX 5070 Ti (Blackwell) support.
"""
import timeit
import json
from datasets import Dataset

# Load GPFS dataset
print('Loading GPFS dataset...')
start_time = timeit.default_timer()

qa_pairs = []
with open('gpfs_dataset.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        qa_pairs.append(json.loads(line))

dataset = Dataset.from_list(qa_pairs)
split_dataset = dataset.train_test_split(test_size=0.2)
print(f'Dataset loaded in {timeit.default_timer() - start_time:.1f}s')
print(f'Training samples: {len(split_dataset["train"])}, Test samples: {len(split_dataset["test"])}')

# Model loading
print('\nLoading model...')
start_time = timeit.default_timer()
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

model_checkpoint = 'ibm-granite/granite-3.1-2b-instruct'
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# RTX 5070 Ti works with PyTorch 2.9.1+cu128
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    model_checkpoint,
    quantization_config=bnb_config,
    trust_remote_code=True
)
print(f'Model loaded in {timeit.default_timer() - start_time:.1f}s')

# Sanity check - ask about GPFS before training
print('\n=== Before Training ===')
input_text = '<|start_of_role|>user<|end_of_role|>How do I check network connectivity in GPFS?<|end_of_text|>\n<|start_of_role|>assistant<|end_of_role|>'
inputs = tokenizer(input_text, return_tensors='pt').to(model.device)
outputs = model.generate(**inputs, max_new_tokens=150)
print('Q: How do I check network connectivity in GPFS?')
print('A:', tokenizer.decode(outputs[0], skip_special_tokens=True).split('assistant')[-1].strip())

# Training setup
print('\nSetting up training...')

def formatting_prompts_func(example):
    # Format for granite-3.1 instruction format
    return f"<|start_of_role|>user<|end_of_role|>{example['question']}<|end_of_text|>\n<|start_of_role|>assistant<|end_of_role|>{example['answer']}<|end_of_text|>"

qlora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=['q_proj', 'v_proj'],
    lora_dropout=0.1,
    bias='none'
)

training_args = SFTConfig(
    output_dir='./gpfs_results',
    learning_rate=2e-4,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,  # Multiple epochs since dataset is small
    max_steps=100,  # Quick demo: 100 steps
    logging_steps=10,
    bf16=True,
    report_to='none',
    max_length=512,
    save_steps=50,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=split_dataset['train'],
    eval_dataset=split_dataset['test'],
    processing_class=tokenizer,
    peft_config=qlora_config,
    formatting_func=formatting_prompts_func,
)

# Training
print('\nStarting training...')
start_time = timeit.default_timer()
trainer.train()
print(f'Training completed in {timeit.default_timer() - start_time:.1f}s')

# Save the model
trainer.save_model('./gpfs_results/final')
print('Model saved to ./gpfs_results/final')

# Evaluation - test with GPFS questions
print('\n=== After Training ===')

test_questions = [
    "How do I check network connectivity in GPFS?",
    "What is mmdiag used for?",
    "How do I deploy the IBM Spectrum Scale CSI driver?",
]

for question in test_questions:
    input_text = f'<|start_of_role|>user<|end_of_role|>{question}<|end_of_text|>\n<|start_of_role|>assistant<|end_of_role|>'
    inputs = tokenizer(input_text, return_tensors='pt').to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=200)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True).split('assistant')[-1].strip()
    print(f'\nQ: {question}')
    print(f'A: {answer[:300]}...' if len(answer) > 300 else f'A: {answer}')

print('\nDone! GPFS-tuned model saved to ./gpfs_results/final')
