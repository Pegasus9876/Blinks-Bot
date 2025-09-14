import os
import re
import json
import requests
from typing import Optional, Dict, Set


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOKEN_FILE = os.path.join(ROOT, "data", "tokens.json")
LITE_SEARCH_URL = "https://lite-api.jup.ag/tokens/v2/search?query="
HTTP_TIMEOUT = 8


PRELOAD_TOKENS = True

FILLER_WORDS = {
    "CAN", "YOU", "SWAP", "SOME", "A", "AN", "THE", "PLEASE", "ME", "MY",
    "TO", "FOR", "HELP", "HELPME", "ON", "WE", "CHECK", "BALANCE", "WHAT", "IS", "OF", "BUY", "SEND", "STAKE", "DONATE"
}

BUILTIN_TOKENS = {"SOL", "USDC", "USDT", "ETH", "BTC", "BONK", "JUP", "RAY", "WIF", "MSOL"}
TOKEN_SYNONYMS = {
    "ETHEREUM": "ETH",
    "ETHER": "ETH",
    "BITCOIN": "BTC",
    "SOLANA": "SOL",
    "USD COIN": "USDC",
    "WRAPPED SOL": "SOL",
}

BONK_LOCK_URL = (
    "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fbonkblinks.com"
    "%2Fapi%2Factions%2Flock%3F_brf%3Da0898550-e7ec-408d-b721-fca000769498"
    "%26_bin%3Dffafbecd-bb86-435a-8722-e45bf139eab5"
)


_cached_tokens: Optional[Set[str]] = None


def load_cached_tokens() -> Set[str]:
    global _cached_tokens
    if _cached_tokens is not None:
        return _cached_tokens

    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    _cached_tokens = {s.upper() for s in data}
                elif isinstance(data, dict):
                    found = []
                    for v in data.values():
                        if isinstance(v, list):
                            found = v
                            break
                    _cached_tokens = {s.upper() for s in found} if found else set(BUILTIN_TOKENS)
                else:
                    _cached_tokens = set(BUILTIN_TOKENS)
                print(f"Loaded {len(_cached_tokens)} tokens from cache")
                return _cached_tokens
    except Exception as e:
        print(f"Failed to load token cache: {e}")

    _cached_tokens = set(BUILTIN_TOKENS)
    return _cached_tokens


def save_token_to_cache(symbol: str):
    s = symbol.upper().strip()
    if not s:
        return
    tokens = load_cached_tokens()
    if s in tokens:
        return
    tokens.add(s)
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(sorted(tokens), f, indent=2)


def search_jupiter_lite(symbol: str) -> bool:
    try:
        resp = requests.get(LITE_SEARCH_URL + symbol, timeout=HTTP_TIMEOUT)
        if resp.status_code != 200:
            return False
        data = resp.json()
        for token in data:
            if token.get("symbol", "").upper() == symbol.upper():
                return True
    except Exception:
        pass
    return False


def is_valid_token(symbol: str, allow_fallback_api: bool = True) -> bool:
    if not symbol:
        return False
    s = symbol.upper().strip()
    if s in TOKEN_SYNONYMS:
        s = TOKEN_SYNONYMS[s]
    tokens = load_cached_tokens()
    if s in tokens:
        return True
    if allow_fallback_api:
        found = search_jupiter_lite(s)
        if found:
            save_token_to_cache(s)
            load_cached_tokens().add(s)
            return True
    return False

def normalize_text(text: str) -> str:
    return text.upper().strip()


def words_from_text(text: str):
    return re.findall(r"[A-Z0-9]+", normalize_text(text))


def extract_tokens(text: str):
    words = words_from_text(text)
    tokens_found = []
    for w in words:
        if w in FILLER_WORDS:
            continue
        candidate = TOKEN_SYNONYMS.get(w, w)
        if is_valid_token(candidate, allow_fallback_api=False):
            tokens_found.append(candidate)
            continue
        if is_valid_token(candidate, allow_fallback_api=True):
            tokens_found.append(candidate)
            continue
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

def parse_swap_intent(text: str):
    amount = extract_amount(text)
    tokens = extract_tokens(text)

    match = re.search(
        r"swap\s*(\d+(\.\d+)?)?\s*([A-Za-z0-9]+)\s*(to|for)\s*([A-Za-z0-9]+)",
        text, re.IGNORECASE
    )
    if match:
        amount = float(match.group(1)) if match.group(1) else amount
        from_tok = TOKEN_SYNONYMS.get(match.group(3).upper(), match.group(3).upper())
        to_tok = TOKEN_SYNONYMS.get(match.group(5).upper(), match.group(5).upper())
        if is_valid_token(from_tok) and is_valid_token(to_tok):
            url = f"https://jup.ag/swap/{from_tok}-{to_tok}"
            if amount:
                url += f"?amount={amount}"
            return {"action": "swap", "amount": amount, "from_token": from_tok, "to_token": to_tok, "url": url}

    if len(tokens) >= 2:
        from_token, to_token = tokens[0], tokens[1]
        url = f"https://jup.ag/swap/{from_token}-{to_token}"
        if amount:
            url += f"?amount={amount}"
        return {"action": "swap", "amount": amount, "from_token": from_token, "to_token": to_token, "url": url}
    return None


def parse_balance_intent(text: str):
    wallet = extract_wallet_address(text)
    match = re.search(r"(balance\s*(of)?\s*([A-Z0-9]+))|([A-Z0-9]+)\s*balance", normalize_text(text))
    token_candidate = match.group(3) if match and match.group(3) else None
    token = token_candidate if token_candidate and is_valid_token(token_candidate) else (extract_tokens(text)[0] if extract_tokens(text) else None)
    if wallet and token:
        return {"action": "balance", "wallet": wallet, "token": token,
                "url": f"https://solscan.io/account/{wallet}?token={token}"}
    return None


TOKEN_TO_COINGECKO = {
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "SOL": "solana",
    "USDC": "usd-coin",
    "JUP": "jupiter",
}

def parse_price_intent(text: str):
    tokens = extract_tokens(text)  # ["ETH"] or ["JUP"], etc.
    token = tokens[0] if tokens else "PRICE"
    coingecko_id = TOKEN_TO_COINGECKO.get(token, "price")
    return {
        "action": "price",
        "token": token,
        "url": f"https://www.coingecko.com/en/coins/{coingecko_id}"
    }


def parse_transfer_intent(text: str):
    wallet = extract_wallet_address(text)
    amount = extract_amount(text)
    match = re.search(r"(\d+(\.\d+)?)?\s*([A-Z0-9]+)?\s*to\s*[1-9A-HJ-NP-Za-km-z]{32,44}", normalize_text(text))
    token_candidate = match.group(3) if match and match.group(3) else None
    token = token_candidate if token_candidate and is_valid_token(token_candidate) else (extract_tokens(text)[0] if extract_tokens(text) else None)
    if wallet and token and amount:
        return {"action": "transfer", "wallet": wallet, "token": token, "amount": amount,
                "url": f"https://solscan.io/account/{wallet}"}
    return None


def parse_buy_intent(text: str):
    domain = extract_domain(text)
    tokens = extract_tokens(text)
    if domain:
        return {"action": "buy", "domain": domain,
                "url": f"https://solscan.io/domain/{domain}"}
    if tokens:
        token = tokens[0]
        return {"action": "buy", "token": token,
                "url": f"https://jup.ag/swap/USDC-{token}"}
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


def parse_donation_intent(text: str):
    wallet = extract_wallet_address(text)
    tokens = extract_tokens(text)
    return {"action": "donation", "wallet": wallet, "token": tokens,
            "url": f"https://solscan.io/account/{wallet}"} if wallet else None



def parse_game_intent(text: str):
    text_upper = normalize_text(text)
    if "COIN" in text_upper and "FLIP" in text_upper:
        return {"action": "game", "game": "coin_flip",
                "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fflip.sendarcade.fun%2Fapi%2Factions%2Fflip%3F_brf%3D9867785e-044d-4158-9b07-80a00db05052%26_bin%3D9f415adc-978d-4bfd-a5b8-66b0ca13f37e"}
    if "ROCK" in text_upper and "PAPER" in text_upper:
        return {"action": "game", "game": "rock_paper_scissors",
                "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Frps.sendarcade.fun%2Fapi%2Factions%2Frps%3F_brf%3D5056cb65-8e5f-4812-bbfb-c887f555e91f%26_bin%3D9d908db2-5996-4c4c-9650-37530601e8e0"}
    if "SNAKE" in text_upper and "LADDERS" in text_upper:
        return {"action": "game", "game": "snake_ladders",
                "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fsnakes.sendarcade.fun%2Fapi%2Factions%2Fgame%3F_brf%3Df722eb4a-297a-447b-aa1f-62f870b789fe%26_bin%3Dab63b0bf-abbd-4354-bb55-855309118e6a"}
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

def parse_domain_intent(text: str):
    """
    Extract a domain like abhi.sol, xyz.eth, etc., from the text.
    Returns a dict with action, domain, and URL if found.
    """
    domain = extract_domain(text)
    if domain:
        return {
            "action": "domain",
            "domain": domain,
            "url": f"https://solscan.io/domain/{domain}"
        }
    return None

def parse_buy_intent(text: str):
    domain = extract_domain(text)
    if domain:
        return {
            "action": "buy",
            "domain": domain,
            "url": f"https://solscan.io/domain/{domain}"
        }

    tokens = extract_tokens(text)
    if tokens:
        token = tokens[0]  
        return {
            "action": "buy",
            "token": token,
            "url": f"https://jup.ag/swap/USDC-{token}"
        }

    return None

def parse_intent(intent: str, text: str) -> Optional[Dict]:
    static_result = parse_static_intent(text)
    if static_result:
        return static_result

    i = intent.lower() if intent else ""
    if i == "swap":
        return parse_swap_intent(text)
    if i == "balance":
        return parse_balance_intent(text)
    if i == "price":
        return parse_price_intent(text)
    if i == "domain":
        return parse_domain_intent(text)
    if i == "transfer":
        return parse_transfer_intent(text)
    if i == "buy":
        if extract_domain(text):
            return parse_domain_intent(text)
        return parse_buy_intent(text)
    if i == "stake":
        return parse_stake_intent(text)
    if i == "donation":
        return parse_donation_intent(text)
    if i == "game":
        return parse_game_intent(text)

    return {"error": f"Unknown intent: {intent}"}

if PRELOAD_TOKENS:
    load_cached_tokens()
