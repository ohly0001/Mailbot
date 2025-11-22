from transformers import AutoModelForCausalLM, AutoTokenizer

class ai_controller:
	def __init__(self, model_name: str):
		try:
			self.model_name = model_name
			self.model = AutoModelForCausalLM.from_pretrained(model_name)
			self.tokenizer = AutoTokenizer.from_pretrained(model_name)
		except Exception as e:
			print(f"Failed to setup transformer: {e}")
			exit(3)

	def call(self, msg_stack: list[str]):
		pass