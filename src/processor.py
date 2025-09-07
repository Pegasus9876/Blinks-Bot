from .intent_recognition import get_intent
from .parameter_extractors import (
    extract_parameters_swap,
    extract_parameters_buy,
    extract_parameters_stake,
    extract_parameters_donation,
    extract_parameters_game,
    extract_parameters_static
)

def process_query(query: str) -> dict:
    intent = get_intent(query)
    if not intent:
        return {"error": "No matching intent found"}

    if intent == "swap":
        return {"tool": "swap", **extract_parameters_swap(query)}
    elif intent == "buy":
        return {"tool": "buy", **extract_parameters_buy(query)}
    elif intent == "stake":
        return {"tool": "stake", **extract_parameters_stake(query)}
    elif intent == "donation":
        return {"tool": "donation", **extract_parameters_donation(query)}
    elif intent == "game":
        return {"tool": "game", **extract_parameters_game(query)}
    elif intent == "static":
        return {"tool": "static", **extract_parameters_static(query)}

    return {"error": "Unsupported intent"}
