from openai import OpenAI

from .llm import LLM


class OpenAILLM(LLM):
    def __init__(self,
                 model_name_or_path: str,
                 api_key: str,
                 temperature: int = 0,
                 max_tokens: int = 512) -> None:
        super(OpenAILLM, self).__init__()
        self.model_name_or_path = model_name_or_path
        if not api_key.startswith("sk-"):
            raise ValueError("OpenAI API key should start with sk-")
        if self.model_name_or_path not in ["gpt-3.5-turbo", "gpt-4"]:
            raise ValueError(
                "OpenAI model path should be gpt-3.5-turbo or gpt-4.")
        self.client = OpenAI(api_key=api_key)
        
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, input: str) -> str:
        results = self.client.chat.completions.create(
            model=self.model_name_or_path,
            messages=[
                {"role": "system", "content": "you are helpful assistant."},
                {"role": "user", "content": input},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return results.choices[0].message.content