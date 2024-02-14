import csv
import os
import time
from typing import List, TYPE_CHECKING

from click import prompt

from .llms import LLM
from .utils.predict import Predictor
from .utils import get_logger, synthesis_message

if TYPE_CHECKING:
    from selection import SelectPolicy
    from mutator import MutatePolicy


class PromptNode:
    """Prompt Node
    
    Manage nodes in tree format. Each node represents a jailbreak prompt, child nodes mutate based on parent nodes.
    The selected node will undergo several mutations, and only the mutants that have successfully jailibreak will be retained,
    `response` will store the reply after sending the variant to LLMs,
    the corresponding label of the reply is stored in `results`.
    
    Attributes:
        prompt (str): jailbreak prompt.
        parent (PromptNode, optional): Based on which node is mutated. Defaults to None.
        mutator (str, optional): mutation method. Defaults to None.
        response (List[str], optional): LLMs's response to prompt that consisting of `prompt`. Default to None.
        results (List[int], optional): The label corresponding to the response. Default to None.
        visited_num (int): The number of times a node is selected in the seed selection strategy.
        children (list[PromptNode]): Nodes mutated based on this node.
        index (int): Node index: 1,2,3,4...
    """
    
    def __init__(self,
                 prompt: str,
                 parent: "PromptNode" = None,
                 responses: List[str] = None,
                 results: List[int] = None):
        self.prompt: str = prompt
        self.parent: "PromptNode" = parent
        self.response: List[str] = responses
        self.results: List[int] = results  # The judgement of eacg response.
        
        self.visited_num: int = 0
        self.children: List["PromptNode"] = []
        self.level: int = 0 if parent is None else parent.level + 1
        self._index: int = None
    
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, index: int):
        self._index = index
        if self.parent is not None:
            self.parent.children.append(self)
    
    @property
    def num_jailbreak(self):
        return sum(self.results)


class Fuzzer:
    def __init__(self,
                 target: LLM,
                 questions: List[str],
                 predictor: Predictor,
                 initial_seed: List[str],
                 mutate_policy: "MutatePolicy",
                 select_policy: "SelectPolicy",
                 max_jailbreak: int = -1,
                 max_iteration: int = -1,
                 result_file: str = None,
                 generate_in_batch: bool = False):
        self.target: LLM = target
        self.questions: List[str] = questions
        self.predictor: Predictor = predictor
        self.prompt_nodes: List[PromptNode] = [
            PromptNode(prompt) for prompt in initial_seed
        ]
        self.initial_prompt_nodes = self.prompt_nodes.copy()
        
        for i, prompt_node in enumerate(self.prompt_nodes):
            prompt_node.index = i
        
        self.mutate_policy = mutate_policy
        self.select_policy = select_policy
        
        self.cur_jailbreak = 0
        self.cur_iteration = 0
        
        self.max_jailbreak = len(questions) if max_jailbreak == -1 and max_iteration == -1 else max_jailbreak
        self.max_iteration = max_iteration
        
        if result_file is None:
            result_file = os.path.join(f"results-{time.strftime('%m-%d-%H-%M', time.localtime())}.csv")
        
        self.raw_fp = open(result_file, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.raw_fp)
        self.writer.writerow(
            ["index", "prompt", "response"]
        )
        self.raw_fp.flush()
        self.generate_in_batch = False
        if len(self.questions) > 0 and generate_in_batch is True:
            self.generate_in_batch = True
        
        self.info_logger = get_logger("info")
        self.debug_logger = get_logger("debug")
        
        self.setup()
    
    def setup(self):
        self.select_policy.fuzzer = self
        self.mutate_policy.fuzzer = self
    
    def is_stop(self):
        checks = [
            ("max_jailbreak", "cur_jailbreak"),
            ("max_iteration", "cur_iteration"),
        ]
        return any(
            getattr(self, max_attr) != -1 and getattr(self, cur_attr) >= getattr(self, max_attr) 
            for max_attr, cur_attr in checks
        )
    
    def run(self):
        self.info_logger.info("Fuzzing Test Start!")
        try:
            while not self.is_stop():
                self.info_logger.info(f"Iteartion {self.cur_iteration}: {self.cur_jailbreak}")
                seed = self.select_policy.select()
                self.info_logger.info(f"The selected node:\n{seed.prompt}")
                mutated_result = self.mutate_policy.mutate_single(seed)
                self.info_logger.info(f"The mutation:\n{mutated_result.prompt}")
                self.evaluate(mutated_result)
                self.update(mutated_result)
        except Exception as e:
            self.info_logger.info(f"Fuzzingn test undergo an error: {e}")
            raise e
        else:
            self.info_logger.info("Fuzzing test finish!")
        finally:
            self.raw_fp.close()
    
    def evaluate(self, prompt_node: PromptNode):
        responses = []
        messages = []
        for question in self.questions:
            message = synthesis_message(question, prompt_node.prompt)
            if message is None:  # The prompt is not valid
                prompt_node.response = []
                prompt_node.results = []
                break
            if not self.generate_in_batch:
                response = self.target.generate(message)
                self.info_logger.debug(f"The response for question {question}: \n{response}")
                responses.append(response)
            else:
                messages.append(message)
        else:
            if self.generate_in_batch:
                responses = self.target.generate_batch(messages)
            
            prompt_node.response = responses
            prompt_node.results = self.predictor.predict_batch(responses)
    
    def update(self, prompt_node: PromptNode):
        self.cur_iteration += 1
        if prompt_node.num_jailbreak > 0:
            prompt_node.index = len(self.prompt_nodes)
            self.prompt_nodes.append(prompt_node)
            row = [prompt_node.index, prompt_node.prompt]
            row.extend(prompt_node.response)
            self.writer.writerow(row)
            self.info_logger.info("The mutation is valid.")
        else:
            self.info_logger.info("The mutation is invalid.")
        self.cur_jailbreak += prompt_node.num_jailbreak
        self.select_policy.update(prompt_node)