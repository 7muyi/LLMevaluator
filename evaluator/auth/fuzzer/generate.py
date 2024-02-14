import csv
from typing import Dict

from .mutator import MutateRandomSinglePolicy, OpenAIMutator
from .selection import RandomSelectPolicy, RoundRobinSelectPolicy, MCTSExploreSelectPolicy
from .llms.llm import LocalLLM, OpenAILLM
from .utils.predict import OpenAIPredictor
from .fuzzer import Fuzzer


def generate_sample(seed_path: str,
                    question_path: str,
                    number: int,
                    tar_model: Dict[str, str],
                    select_policy: str,
                    stop_condition: str,
                    mut_model_name: str = "gpt-3.5-turbo",
                    alpha: int = 0.1,
                    beta: int = 0.2):
    if tar_model["name"] == "gpt-3.5-turbo":
        tar_model = OpenAILLM(tar_model["name"], "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")
    else:
        tar_model = LocalLLM(url=tar_model["url"],
                             return_format=tar_model["return_format"],
                             access_token=tar_model["access_token"])
    
    assert mut_model_name in ("gpt-3.5-turbo"), "The model for mutation must be one of `gpt-3.5-turbo`."
    if mut_model_name == "gpt-3.5-turbo":
        mut_model = OpenAILLM(mut_model_name, "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")
    
    assert select_policy in ("Random", "Round robin", "MCTS-Explore"), ("The selection poilcy must be one of"
        "`Random`, `Roud robin` or `MCTS-Explore`.")
    if select_policy == "Random":
        select = RandomSelectPolicy()
    elif select_policy == "Round robin":
        select = RoundRobinSelectPolicy()
    else:
        select = MCTSExploreSelectPolicy(alpha=alpha, beta=beta)
    
    assert stop_condition in ("max-iteration", "max-vulnerability"), "The stop condition must be `max-iteration` or `max-vulnerability`."
    if stop_condition == "max-vulnerability":
        max_jailbreak = number
        max_iteration = -1
    else:
        max_jailbreak = -1
        max_iteration = number
    
    predictor = OpenAIPredictor("gpt-3.5-turbo", "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")
    
    initial_seed = []
    
    with open(seed_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # skip title row
        next(reader)
        
        for row in reader:
            initial_seed.append(row[1])
    question_list = []
    
    with open(question_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        # skip title row
        next(reader)
        
        for row in reader:
            question_list.append(row[1])
    
    fuzzer = Fuzzer(
        questions=question_list,
        target=tar_model,
        predictor=predictor,
        initial_seed=initial_seed,
        mutate_policy=MutateRandomSinglePolicy(
            OpenAIMutator(mut_model, temperature=1),
            concatentate=False,
        ),
        select_policy=select,
        energy=1,
        max_jailbreak=max_jailbreak,
        max_iteration=max_iteration,
        generate_in_batch=False,
    )
    
    fuzzer.run()