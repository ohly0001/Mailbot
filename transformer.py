from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch

# model used: meta-llama/Llama-2-7b-chat-hf

class ai_controller:
    SYS_HEADER = "You are a helpful email correspondent. The person you are replying to is {}."

    def __init__(self, model_name: str, max_tokens_output: int):
        try:
            self.model_name = model_name
            self.max_tokens_output = max_tokens_output

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )

            # Use model's max context length if available
            if hasattr(self.tokenizer, "model_max_length"):
                self.max_tokens_context = self.tokenizer.model_max_length
            else:
                # fallback to 4096 if unknown
                self.max_tokens_context = 4096

        except Exception as e:
            print(f"Failed to setup transformer: {e}")
            exit(3)

    def call(self, msg_stack: list[dict[str, str]]):
        if not msg_stack:
            return None
        
        # Build conversation
        conversation = []

        # System
        system_msg = self.SYS_HEADER.format(msg_stack[-1]["sender_name"])
        conversation.append({"role": "system", "content": system_msg})

        # Add user messages (newest first, oldest last, clipped by token budget)
        total_tokens = 0
        reversed_msgs = list(reversed(msg_stack))

        for msg in reversed_msgs:
            # Estimate cost of adding this message
            encoded = self.tokenizer.encode(msg["body_text"], add_special_tokens=False)
            if total_tokens + len(encoded) > self.max_tokens_context:
                break

            total_tokens += len(encoded)

            conversation.insert(1, {
                "role": "user",
                "content": msg["body_text"]
            })

        # Convert conversation to the model’s required format
        prompt = self.tokenizer.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.model.device)

        
        # Generation config
        gen_cfg = GenerationConfig(
            max_new_tokens=self.max_tokens_output,
            do_sample=False,
            temperature=0.0
        )

        # Run inference
        output = self.model.generate(
            **inputs,
            generation_config=gen_cfg
        )

        # Decode only the new tokens
        generated_text = self.tokenizer.decode(
            output[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()

        return generated_text