import sys
import os

# Ensure src is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intent_recognition import classify_intent
from src.entities import parse_intent

# -------------------------
# Test queries
# -------------------------
QUERIES = [
    "open Keystone Wallet",
    "deposit funds on Lulo",
    "lock my BONK for 12 months",
    "swap 10 usdc to sol",
    "swap usdc to eth",
    "swap 5 bitcoin to usdt",
    "check balance of usdc in wallet 9jHi87Fe7YTYpLjVK5hxt3FZNYG6kSEUew4h2zqdcJYZ",
    "what is the price of JUP?",
    "price of bitcoin",
    "price of ethereum",
    "buy abhi.sol",
    "domain abhi.sol",
    "send 50 usdc to 9jHi87Fe7YTYpLjVK5hxt3FZNYG6kSEUew4h2zqdcJYZ",
    "buy SOL",
    "buy ethereum",
    "stake BONK",
    "stake solana",
    "donate to 9jHi87Fe7YTYpLjVK5hxt3FZNYG6kSEUew4h2zqdcJYZ",
    "Create a Blink for a coin flip game",
    "Create a Blink for rock paper scissors",
    "Create a Blink for snake and ladders",
]

# -------------------------
# Runner
# -------------------------
def run_tests():
    for query in QUERIES:
        print("-" * 50)
        print(f"Query: {query}")

        # Step 1: classify intent
        intent = classify_intent(query)
        print(f"Detected intent: {intent}")

        # Step 2: parse entities/params
        result = parse_intent(intent, query) if intent else None
        print(f"Result: {result}")

        # Step 3: Show URL (if available)
        if result and isinstance(result, dict) and "url" in result:
            print(f"👉 Link: {result['url']}")


if __name__ == "__main__":
    run_tests()
