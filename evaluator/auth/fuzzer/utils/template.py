QUESTION_PLACEHOLDER = "[INSERT PROMPT HERE]"

def synthesis_message(question, prompt):
    """Construction prompt
    
    Construction the prompt by inserting the question into the prompt template at the position [INSERT PROMPT HERE].
    
    Args:
        question (str): Prompt template.
        prompt (str): Questions to be inserted.
    
    Returns:
        str: Prompt generated.
    """
    if QUESTION_PLACEHOLDER not in prompt:
        return None
    
    return prompt.replace(QUESTION_PLACEHOLDER, question)