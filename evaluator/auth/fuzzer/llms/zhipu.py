from typing import List

from zhipuai import ZhipuAI

from .llm import LLM


class ZhipuLLM(LLM):
    def __init__(self):
        self.client = ZhipuAI(api_key="Your API Key")
    
    def generate(self, input: str) -> str:
        response = self.client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "user", "content": input}
            ],
        )
        return response.choices[0].message.content