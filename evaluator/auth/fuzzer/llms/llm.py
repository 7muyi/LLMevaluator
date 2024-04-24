import concurrent.futures
import json
from abc import ABC, abstractmethod
from typing import List

import requests

from ..utils.log_config import get_logger

info_logger = get_logger("info")

class LLM(ABC):
    @abstractmethod
    def generate(self, input: str) -> str:
        pass
    
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
                 access_token: str = None,
                 headers_or_url: bool = "headers",
                 **kwargs) -> None:
        """Initialize invoke strategy
        
        Initialize invoking information includes query chain, url whose format is {url}access_token={access_token} .
        
        Args:
            url (str): accessing address provider by the third-part LLM provider.
            access_token (str): access token.
            query_chain (str): the path getting the message from the response.
            headers_or_url(str): access token transmission method, headers in url.
        """
        super(LLMFromAPI, self).__init__()
        self.model_name_or_path = model_name_or_path
        self.url = url
        # self.url = url if not access_token else f"{url}?access_token={access_token}"
        self.access_token = access_token
        self.headers_or_url = headers_or_url
        self.query_chain = return_format.split(".")
        self.data = kwargs
    
    def generate(self, input: str) -> str:
        payload = {
            "messages": [
                {"role": "user", "content": input}
            ]
        }
        if self.data:
            payload["model"] = self.data["model"]
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_token:
            if self.headers_or_url == "headers":
                headers["Authorization"] = self.access_token
            elif self.headers_or_url == "url":
                self.url = f"{self.url}?access_token={self.access_token}"
        try:
            response = requests.request("POST", self.url, headers=headers, data=json.dumps(payload))
            if response.status_code != 200 :
                raise LLMError(f"Connection error: status code{response.status_code}")
            res = response.json()
            for query in self.query_chain:
                if query.isdigit():
                    if isinstance(res, list):
                        res = res[int(query)]
                    else:
                        raise APICallError("Query chain does not match result")
                else:
                    res = res.get(query)
                    if not res:
                        raise APICallError("Query chain does not match result")
            else:
                return res
        except Exception as e:
            raise APICallError(e)


class LLMError(Exception):
    def __init__(self, message: str) -> None:
        super(LLMError, self).__init__(message)
        self.message = message
    
    def __str__(self) -> str:
        return f"LLMError: {self.message}"


class APICallError(LLMError):
    def __init__(self, message: str) -> None:
        super(APICallError, self).__init__(message)
        self.message = f"API call failed due to {message}"
    
    def __str__(self) -> str:
        return f"APICallError: {self.message}"