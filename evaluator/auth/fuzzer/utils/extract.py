def extract(input: str, start: str, end: str):
    start_index = input.find(start)
    end_index = input.rfind(end, start_index + len(start))
    
    if start_index == -1 or end_index == -1:
        return input.replace(start, "").replace(end, "")
    
    return input[start_index + len(start): end_index]

def clean(input: str):
    return input.replace("\n\n", "\n")