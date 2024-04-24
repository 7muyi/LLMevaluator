import random
from abc import ABC, abstractmethod
from typing import List

import numpy as np

from .fuzzer import Fuzzer, PromptNode


class SelectPolicy(ABC):
    def __init__(self) -> None:
        self._fuzzer = None
    
    @abstractmethod
    def select(self, prompt_nodes: List[PromptNode]) -> PromptNode:
        pass
    
    def update(self, prompt_nodes: List[PromptNode]) -> None:
        pass
    
    @property
    def fuzzer(self):
        return self._fuzzer
    
    @fuzzer.setter
    def fuzzer(self, fuzzer: Fuzzer):
        self._fuzzer = fuzzer


class RoundRobinSelectPolicy(SelectPolicy):
    def __init__(self) -> None:
        super(RoundRobinSelectPolicy, self).__init__()
        self.index: int = 0
    
    def select(self) -> PromptNode:
        seed = self.fuzzer.prompt_nodes[self.index]
        seed.visited_num += 1
        return seed
    
    def update(self, prompt_nodes: List[PromptNode]) -> None:
        self.index = (self.index - 1 + len(prompt_nodes)) % len(prompt_nodes)


class RandomSelectPolicy(SelectPolicy):
    def __init__(self) -> None:
        super(RandomSelectPolicy, self).__init__()
    
    def select(self,) -> PromptNode:
        seed = random.choice(self.fuzzer.prompt_nodes)
        seed.visited_num += 1
        return seed



class MCTSExploreSelectPolicy(SelectPolicy):
    """Implementation of Monte Carlo tree search algorithm
    
    Find the child node with the highest UCT score and
    continue iterating until it reaches a leaf node or exits randomly.
    """
    def __init__(self,
                 ratio: float = 0.5,
                 alpha: float = 0.1,
                 beta: float = 0.2,) -> None:
        super(MCTSExploreSelectPolicy, self).__init__()
        self.ratio = ratio
        self.alpha = alpha
        self.beta = beta
        
        self.step = 0
        self.select_path = []  # Search parh for each iteration. The last node selected is the final node selected.
        self.rewards = []  # Record rewards for each node.
    
    def select(self) -> PromptNode:
        self.step += 1
        
        # Update the rewards list to ensure that each node has a corresponding reward in the list.
        if len(self.fuzzer.prompt_nodes) > len(self.rewards):
            self.rewards.extend([0 for _ in range(len(self.fuzzer.prompt_nodes) - len(self.rewards))])
        
        self.select_path.clear()
        
        # Caculate the UCT score.
        def uct_score(prompt_node: PromptNode) -> float:
            return (
                self.rewards[prompt_node.index] / (prompt_node.visited_num + 1) +
                self.ratio * np.sqrt(2 * np.log(self.step)) / (prompt_node.visited_num + 0.01)
            )
        
        # Select the initial node(like roots) with the highest UCT score.
        cur = max(self.fuzzer.initial_prompt_nodes, key=uct_score)
        self.select_path.append(cur)
        
        # Iterate until the node is leaf
        while len(cur.children) > 0:
            # Exist randomly to avoid selecting the leaf every time to increase diversity.
            if np.random.rand() < self.alpha:  
                break
            
            cur = max(cur.children, key=uct_score)
            cur.visited_num += 1
            self.select_path.append(cur)
        
        self.last_choice_index = cur.index
        return cur
    
    def update(self, prompt_node: PromptNode):
        succ_num = prompt_node.num_jailbreak
        level = self.fuzzer.prompt_nodes[self.last_choice_index].level
        
        reward = succ_num / len(self.fuzzer.questions)
        for prompt_node in self.select_path:
            self.rewards[prompt_node.index] += reward * max(self.beta, (1 - 0.1 * level))



class MCTSExploreSelectPolicy(SelectPolicy):
    def __init__(self,
                 ratio: float = 0.5,
                 alpha: float = 0.1,
                 beta: float = 0.2,) -> None:
        super(MCTSExploreSelectPolicy, self).__init__()
        self.ratio = ratio
        self.alpha = alpha
        self.beta = beta
        
        self.step = 0
        self.select_path = []
        self.rewards = []
    
    def select(self) -> PromptNode:
        self.step += 1
        if len(self.fuzzer.prompt_nodes) > len(self.rewards):
            self.rewards.extend([0 for _ in range(len(self.fuzzer.prompt_nodes) - len(self.rewards))])
        
        self.select_path.clear()
        def uct_score(prompt_node: PromptNode) -> float:
            return (
                self.rewards[prompt_node.index] / (prompt_node.visited_num + 1) +
                self.ratio * np.sqrt(2 * np.log(self.step)) / (prompt_node.visited_num + 0.01)
            )
        cur = max(self.fuzzer.initial_prompt_nodes, key=uct_score)
        self.select_path.append(cur)
        while len(cur.children) > 0:
            if np.random.rand() < self.alpha:  
                break
            
            cur = max(cur.children, key=uct_score)
            cur.visited_num += 1
            self.select_path.append(cur)
        
        self.last_choice_index = cur.index
        return cur
    
    def update(self, prompt_node: PromptNode):
        succ_num = prompt_node.num_jailbreak
        level = self.fuzzer.prompt_nodes[self.last_choice_index].level
        
        reward = succ_num / len(self.fuzzer.questions)
        for prompt_node in self.select_path:
            self.rewards[prompt_node.index] += reward * max(self.beta, (1 - 0.1 * level))