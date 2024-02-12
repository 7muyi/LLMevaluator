import json
import time
import requests
from typing import List
import concurrent.futures
from abc import ABC, abstractmethod

from ..utils.log_config import get_logger

from openai import OpenAI


info_logger = get_logger("info")

class LLM(ABC):
    @abstractmethod
    def generate(self, input: str) -> str:
        pass
    
    @abstractmethod
    def generate_batch(self, inputs: List[str]) -> List[str]:
        pass

class OpenAILLM(LLM):
    def __init__(self,
                 model_name_or_path: str,
                 api_key: str,
                 temperature: int = 0,
                 max_tokens: int = 512) -> None:
        super(OpenAILLM, self).__init__()
        
        if not api_key.startswith("sk-"):
            raise ValueError("OpenAI API key should start with sk-")
        if self.model_name_or_path not in ["gpt-3.5-turbo", "gpt-4"]:
            raise ValueError(
                "OpenAI model path should be gpt-3.5-turbo or gpt-4.")
        self.client = OpenAI(api_key=api_key)
        
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, input: str) -> str:
        for _ in range(10):
            try:
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
            
            except Exception as e:
                info_logger.warning(f"OpenAI API call failed due to {e}. Retrying {_+1} / {10} times...")
                time.sleep(5)
        return ""
    
    def generate_batch(self, inputs: List[str]) -> List[str]:
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, input): input for input in inputs}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results

class LLMFromAPI(LLM):
    """Using API invoke to access third-pary LLM.
    
    Access the LLM through the URL provided by the third pary LLM provider.
    API invokes require url and access token, which are initialized in __init__ function.
    API response are all in JSON format, so the location of the message from response needs to be determined through the
    "query chain".
    The format of "query chain" is [x,x...x,x,x], x represents a key if it's not a number, otherwise it represents a index
    in list. For example if the response in JSON formate as follow:
    {
        "choices": [
            {
                "message": {
                    "content": "reponse which we need."
                }
            }
        ]
    }
    The query chain is ["choices", 0, "content"].
    """
    def __init__(self,
                 model_name_or_path: str,
                 url: str,
                 return_format: str,
                 access_token: str = None) -> None:
        """Initialize invoke strategy
        
        Initialize invoking information includes query chain, url whose format is {url}access_token={access_token} .
        
        Args:
            url (str): accessing address provider by the third-part LLM provider.
            access_token (str): access token.
            query_chain (str): the path getting the message from the response.
        """
        super(LLMFromAPI, self).__init__()
        self.model_name_or_path = model_name_or_path
        self.url = url if not access_token else f"{url}?access_token={access_token}"
        self.query_chain = return_format.split(".")
    
    def generate(self, input: str) -> str:
        payload = json.dumps({
            "messages": [
                {"role": "user", "content": input}
            ]
        })
        headers = {
            "Content-Type": "application/json"
        }
        
        for _ in range(10):
            try:
                response = requests.request("POST", self.url, headers=headers, data=payload)
                res = response.json()
                for query in self.query_chain:
                    if query.isdigit():
                        res = res[query]
                    else:
                        res = res.get(query)
                else:
                    return res
            except Exception as e:
                info_logger.warning(f"{e}. Retrying{_+1} / {10} times...")
                time.sleep(5)
    
    def generate_batch(self, inputs: List[str]) -> List[str]:
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.generate, input): input for input in inputs}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        return results
    
    def is_feasible(self) -> str:
        """Check wheter the API invoke can be invoked normally after initialization.
        
        Returns:
            str: result of judgement. if result is "sucess", it means normal access, otherwise underwent error.
        """
        payload = json.dumps({
            "message": [
                {
                    "role": "user",
                    "content": "你好"
                },
            ]
        })
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.request("POST", self.url, headers=headers, data=payload)
        if response.status_code != 200:
            return f"connection error: {response.status_code}"
        else:
            try:
                res = response.json()
                for query in self.query_chain:
                    if query.isdigit():
                        res = res[query]
                    else:
                        res = res.get(query)
            except Exception as e:
                return f"parsing error or access error: {e}"
            return "success"