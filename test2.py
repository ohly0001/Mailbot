import os
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

load_dotenv()
login(token=os.getenv('ACCESS_TOKEN'))

tokenizer = AutoTokenizer.from_pretrained(os.getenv('MODEL'))
model = AutoModelForCausalLM.from_pretrained(os.getenv('MODEL'))
messages = [
    {"role": "user", "content": "Who are you?"},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=40)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))