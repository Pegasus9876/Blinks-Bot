import re, string

def is_potential_token(word: str) -> bool:
    if 1 <= len(word) <= 6 and word.isalpha():
        return True
    if 32 <= len(word) <= 44 and re.match(r"^[1-9A-HJ-NP-Za-km-z]+$", word):
        return True
    return False

def is_solana_address(word: str) -> bool:
    return 32 <= len(word) <= 44 and re.match(r"^[1-9A-HJ-NP-Za-km-z]+$", word)

def strip_trailing_punctuation(word: str) -> str:
    return word.rstrip(string.punctuation)

def extract_parameters_swap(query: str) -> dict:
    return {}

def extract_parameters_buy(query: str) -> dict:
    return {}

def extract_parameters_stake(query: str) -> dict:
    return {}

def extract_parameters_donation(query: str) -> dict:
    return {}

def extract_parameters_game(query: str) -> dict:
    return {}

def extract_parameters_static(query: str) -> dict:
    return {}
