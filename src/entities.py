# src/entities.py
import re
from typing import Optional, Dict

TOKENS = [
    "USDT", "SOL", "USDC", "USDS", "USDE", "CBBTC", "TRUMP", "REND", "JUP",
    "BNSOL", "LINK", "GRT", "W", "PYTH", "HNT", "MSOL", "BONK", "RAY", "JTO", "WIF",
    "ETH", "BTC"
]

TOKEN_SYNONYMS = {
    "ETHER": "ETH",
    "ETHEREUM": "ETH",
    "BITCOIN": "BTC",
    "SOLANA": "SOL"
}

BONK_LOCK_URL = "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fbonkblinks.com%2Fapi%2Factions%2Flock%3F_brf%3Da0898550-e7ec-408d-b721-fca000769498%26_bin%3Dffafbecd-bb86-435a-8722-e45bf139eab5"

# ---------------- Helpers ----------------
def normalize_text(text: str) -> str:
    return text.upper().strip()

def extract_tokens(text: str):
    text_upper = normalize_text(text)
    tokens_found = []

    for word, token in TOKEN_SYNONYMS.items():
        if word in text_upper:
            tokens_found.append(token)

    for token in TOKENS:
        if token in text_upper:
            tokens_found.append(token)

    return list(dict.fromkeys(tokens_found))

def extract_wallet_address(text: str):
    match = re.search(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b", text)
    return match.group(0) if match else None

def extract_domain(text: str):
    match = re.search(r"\b[\w\d-]+\.(sol|eth|degen|monad|letsbonk)\b", text, re.IGNORECASE)
    return match.group(0) if match else None

def extract_amount(text: str):
    match = re.search(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else None

# ---------------- Parsers ----------------
def parse_swap_intent(text: str):
    amount = extract_amount(text)
    tokens = extract_tokens(text)

    match = re.search(r"swap\s*(\d+(\.\d+)?)?\s*([a-zA-Z]+)\s*(to|for)\s*([a-zA-Z]+)", text, re.IGNORECASE)
    if match:
        amount = float(match.group(1)) if match.group(1) else amount
        from_token = TOKEN_SYNONYMS.get(match.group(3).upper(), match.group(3).upper())
        to_token = TOKEN_SYNONYMS.get(match.group(5).upper(), match.group(5).upper())
        url = f"https://jup.ag/swap/{from_token}-{to_token}"
        if amount:
            url += f"?amount={amount}"
        return {"action": "swap", "amount": amount, "from_token": from_token, "to_token": to_token, "url": url}

    if len(tokens) >= 2:
        from_token, to_token = tokens[0], tokens[1]
        url = f"https://jup.ag/swap/{from_token}-{to_token}"
        if amount:
            url += f"?amount={amount}"
        return {"action": "swap", "amount": amount, "from_token": from_token, "to_token": to_token, "url": url}
    return None

def parse_balance_intent(text: str):
    wallet = extract_wallet_address(text)
    tokens = extract_tokens(text)
    token = tokens[0] if tokens else None
    if wallet and token:
        return {"action": "balance", "wallet": wallet, "token": token,
                "url": f"https://solscan.io/account/{wallet}?token={token}"}
    return None

def parse_price_intent(text: str):
    tokens = extract_tokens(text)
    token = tokens[0] if tokens else None
    if token:
        return {"action": "price", "token": token,
                "url": f"https://www.coingecko.com/en/coins/{token.lower()}"}
    return None

def parse_domain_intent(text: str):
    domain = extract_domain(text)
    if domain:
        return {
            "action": "domain",
            "domain": domain,
            "url": f"https://solscan.io/domain/{domain}"
        }
    return None

def parse_transfer_intent(text: str):
    wallet = extract_wallet_address(text)
    tokens = extract_tokens(text)
    token = tokens[0] if tokens else None
    amount = extract_amount(text)
    if wallet and token and amount:
        return {"action": "transfer", "wallet": wallet, "token": token, "amount": amount,
                "url": f"https://solscan.io/account/{wallet}"}
    return None

def parse_buy_intent(text: str):
    tokens = extract_tokens(text)
    domain = extract_domain(text)
    if tokens:
        token = tokens[0]
        return {"action": "buy", "token": token,
                "url": f"https://jup.ag/swap/USDC-{token}"}
    elif domain:
        return {"action": "buy", "domain": domain,
                "url": f"https://solscan.io/domain/{domain}"}
    return None

def parse_stake_intent(text: str):
    tokens = extract_tokens(text)
    if tokens:
        token = tokens[0]
        if token == "BONK":
            return {"action": "stake", "token": "BONK", "url": BONK_LOCK_URL}
        return {"action": "stake", "token": token,
                "url": f"https://www.marinade.finance/stake/{token.lower()}"}
    return None

def parse_donate_intent(text: str):
    wallet = extract_wallet_address(text)
    if wallet:
        return {"action": "donation", "wallet": wallet,
                "url": f"https://solscan.io/account/{wallet}"}
    return None

def parse_game_intent(text: str):
    text_upper = normalize_text(text)
    if "COIN" in text_upper and "FLIP" in text_upper:
        return {"action": "game", "game": "coin_flip",
                "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fflip.sendarcade.fun%2Fapi%2Factions%2Fflip%3F_brf%3D9867785e-044d-4158-9b07-80a00db05052%26_bin%3D9f415adc-978d-4bfd-a5b8-66b0ca13f37e"}
    elif "ROCK" in text_upper and "PAPER" in text_upper:
        return {"action": "game", "game": "rock_paper_scissors",
                "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Frps.sendarcade.fun%2Fapi%2Factions%2Frps%3F_brf%3D5056cb65-8e5f-4812-bbfb-c887f555e91f%26_bin%3D9d908db2-5996-4c4c-9650-37530601e8e0"}
    elif "SNAKE" in text_upper and "LADDERS" in text_upper:
        return {"action": "game", "game": "snake_ladders",
                "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fsnakes.sendarcade.fun%2Fapi%2Factions%2Fgame%3F_brf%3Df722eb4a-297a-447b-aa1f-62f870b789fe%26_bin%3Dab63b0bf-abbd-4354-bb55-855309118e6a"}
    return None

def parse_donation_intent(text: str):
    wallet = extract_wallet_address(text)
    token = extract_tokens(text)  # optional, user may specify
    if wallet:
        return {
            "action": "donation",
            "wallet": wallet,
            "token": token,
            "url": f"https://solscan.io/account/{wallet}"
        }
    return None

def parse_static_intent(text: str):
    text_upper = normalize_text(text)
    if "STAKE" in text_upper or ("LOCK" in text_upper and "BONK" in text_upper):
        return parse_stake_intent(text)
    if "KEYSTONE" in text_upper and "WALLET" in text_upper:
        return {"action": "static", "type": "wallet", "url": "https://keyst.one/"}
    if "LULO" in text_upper and ("DEPOSIT" in text_upper or "EARN" in text_upper):
        return {"action": "static", "type": "deposit", "url": "https://lulo.fi/deposit"}
    return None

# ---------------- Dispatcher ----------------
def parse_intent(intent: str, text: str):
    intent = intent.lower()

    if intent == "stake":
        return parse_stake_intent(text)

    if intent == "static":
        return parse_static_intent(text)

    if intent == "swap":
        return parse_swap_intent(text)

    if intent == "balance":
        return parse_balance_intent(text)

    if intent == "price":
        return parse_price_intent(text)

    if intent == "buy":
        # special case: if it's a domain, treat as domain intent
        if extract_domain(text):
            return parse_domain_intent(text)
        return parse_buy_intent(text)

    if intent == "transfer":
        return parse_transfer_intent(text)

    if intent == "donation":
        return parse_donation_intent(text)

    if intent == "domain":
        return parse_domain_intent(text)

    if intent == "game":
        return parse_game_intent(text)

    return {"error": f"Unknown intent: {intent}"}