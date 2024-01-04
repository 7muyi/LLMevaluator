import random
import numpy as np
from typing import List

from .fuzzer import PromptNode, Fuzzer


class SelectPolicy:
    def __init__(self, fuzzer: Fuzzer):
        self.fuzzer = fuzzer
    
    def select(self, prompt_nodes: List[PromptNode]) -> PromptNode:
        raise NotImplementedError("SelectPolicy must implement select method")
    
    def update(self, prompt_nodes: List[PromptNode]):
        pass


class RoundRobinSelectPolicy(SelectPolicy):
    def __init__(self, fuzzer: Fuzzer = None):
        super().__init__(fuzzer)
        self.index: int = 0
    
    def select(self) -> PromptNode:
        seed = self.fuzzer.prompt_nodes[self.index]
        seed.visited_num += 1
        return seed
    
    def update(self, prompt_nodes: List[PromptNode]):
        self.index = (self.index - 1 + len(prompt_nodes)) % len(prompt_nodes)


class RandomSelectPolicy(SelectPolicy):
    def __init__(self, fuzzer: Fuzzer = None):
        super().__init__(fuzzer)
    
    def select(self,) -> PromptNode:
        seed = random.choice(self.fuzzer.prompt_nodes)
        seed.visited_num += 1
        return seed


class MCTSExploreSelectPolicy(SelectPolicy):
    def __init__(self,
                 fuzzer: Fuzzer = None,
                 ratio: int = 0.5,
                 alpha: int = 0.1,
                 beta: int = 0.2,):
        super().__init__(fuzzer)
        self.ratio: float = ratio
        self.alpha: float = alpha
        self.beta: float = beta

        self.step: int = 0
        self.select_path: List[PromptNode] = []
        self.rewards: List[float] = []
    
    
    def select(self) -> PromptNode:
        self.step += 1
        
        if len(self.fuzzer.prompt_nodes) > len(self.rewards):
            self.rewards.extend([0 for _ in range(len(self.fuzzer.prompt_nodes) - len(self.rewards))])
        
        self.select_path.clear()
        
        def uct_score(prompt_node: PromptNode) -> float:
            return self.rewards[prompt_node.index] / (prompt_node.visited_num + 1) + \
                self.ratio * np.sqrt(2 * np.log(self.step)) / (prompt_node.visited_num + 0.01)
        
        cur = max(self.fuzzer.initial_prompt_nodes, key=uct_score)
        self.select_path.append(cur)
        
        while len(cur.children) > 0:
            
            if np.random.rand() < self.alpha:
                break
            
            cur = max(cur.children,
                      key=uct_score
            )
            cur.visited_num += 1
            self.select_path.append(cur)
        
        self.last_choice_index = cur.index
        return cur
    
    def update(self, prompt_nodes: List[PromptNode]):
        succ_num = sum([node.num_jailbreak for node in prompt_nodes])
        
        level = self.fuzzer.prompt_nodes[self.last_choice_index].level
        reward = succ_num / (len(prompt_nodes) * len(self.fuzzer.questions))
        for prompt_node in self.select_path:
            self.rewards[prompt_node.index] += reward * \
                max(self.beta, (1 - 0.1 * level))