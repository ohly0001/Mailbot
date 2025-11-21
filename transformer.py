from transformers import AutoModelForCausalLM, AutoTokenizer

class ai_controller:
	def __init__(self, model_name: str):
		self.model_name = model_name
		self.model = AutoModelForCausalLM.from_pretrained(model_name)
		self.tokenizer = AutoTokenizer.from_pretrained(model_name)

	def call(self, msg_stack: list[str]):
		pass