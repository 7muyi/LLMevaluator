import json
import logging
import logging.config


with open("D:/MyWorkspace/project/LLMevaluator/evaluator/auth/fuzzer/config/logging_config.json", "r") as f:
    config = json.load(f)
    
logging.config.dictConfig(config)

def get_logger(level: str = "debug"):
    if not level in ("debug", "info"):
        level = "debug"
    return logging.getLogger(level)