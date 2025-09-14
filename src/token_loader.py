import requests
import json
import re
import os
import argparse

# Data folder in the parent directory (cd ..)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TOKENS_FILE = os.path.join(DATA_DIR, "tokens.json")

TOKEN_LIST_URL = "https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json"
STOPWORDS = {"can", "you", "swap", "some", "to", "for", "a", "the", "me", "please", "on"}


def update_token_list():
    """Download Solana token list and save only symbols to tokens.json"""
    print("Updating token list...")
    resp = requests.get(TOKEN_LIST_URL)
    data = resp.json()

    tokens = sorted(set(token["symbol"].upper() for token in data["tokens"]))

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"Saved {len(tokens)} tokens to {TOKENS_FILE}")


def load_tokens():
    """Load token symbols from file (update if not exists)"""
    if not os.path.exists(TOKENS_FILE):
        update_token_list()
    with open(TOKENS_FILE) as f:
        return set(json.load(f))


def detect_tokens(user_input, tokens):
    """Extract valid token symbols from user query"""
    words = re.findall(r"[A-Za-z0-9]+", user_input.upper())
    detected = [w for w in words if w in tokens and w.lower() not in STOPWORDS]
    return detected


def process_query(query, tokens):
    """Process user input and generate swap URL if possible"""
    detected = detect_tokens(query, tokens)

    if len(detected) >= 2:
        from_token, to_token = detected[0], detected[1]
        url = f"https://jup.ag/swap/{from_token}-{to_token}"
        return {
            "action": "swap",
            "from_token": from_token,
            "to_token": to_token,
            "url": url,
        }
    else:
        return {
            "action": "unknown",
            "tokens_found": detected,
            "message": "Not enough valid tokens found in query",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Refresh token list and exit")
    args = parser.parse_args()

    if args.refresh:
        update_token_list()
        exit(0)

    tokens = load_tokens()

    while True:
        query = input("\nEnter your query: ")
        result = process_query(query, tokens)
        print("Result:", result)
        if result.get("url"):
            print("Swap URL:", result["url"])
