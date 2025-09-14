import sys
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import json
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    GREEN, RED, CYAN, YELLOW, RESET = (
        Fore.GREEN, Fore.RED, Fore.CYAN, Fore.YELLOW, Style.RESET_ALL
    )
except ImportError:
    GREEN = RED = CYAN = YELLOW = RESET = ""
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.intent_recognition import classify_intent
from src.entities import parse_intent
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

def run_tests():
    for idx, query in enumerate(QUERIES, 1):
        print(f"\n{CYAN}{'-'*60}{RESET}")
        print(f"{YELLOW}Test {idx}: {RESET}{query}")

        try:
            # Step 1: classify intent
            intent = classify_intent(query)
            print(f"{GREEN}Detected intent:{RESET} {intent}")

            # Step 2: parse entities/params
            result = parse_intent(intent, query) if intent else None

            if result:
                print(f"{GREEN}Parsed result:{RESET}")
                print(json.dumps(result, indent=2))
                if "url" in result:
                    print(f"{CYAN}Link:{RESET} {result['url']}")
            else:
                print(f"{RED}No result parsed.{RESET}")

        except Exception as e:
            print(f"{RED}Error while processing query:{RESET} {e}")


if __name__ == "__main__":
    run_tests()
