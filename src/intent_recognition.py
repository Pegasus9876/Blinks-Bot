from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from src.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL_NAME
import re

# Load embedding model
_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Static shortcut intents
STATIC_KEYWORDS = {
    "keystone": {"action": "static", "type": "wallet", "url": "https://keyst.one/"},
    "deposit": {"action": "static", "type": "deposit", "url": "https://lulo.fi/deposit"},
    "lock bonk": {
        "action": "stake",
        "token": "BONK",
        "url": "https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fbonkblinks.com%2Fapi%2Factions%2Flock%3F_brf%3Da0898550-e7ec-408d-b721-fca000769498%26_bin%3Dffafbecd-bb86-435a-8722-e45bf139eab5"
    },
}

DOMAIN_PATTERN = re.compile(r"\b[\w\d-]+\.(sol|eth|degen|monad|letsbonk)\b", re.IGNORECASE)

def classify_intent(query: str):
    q_lower = query.lower()

    # 1. Domain check (takes precedence over buy/swap)
    if DOMAIN_PATTERN.search(query):
        return "domain"

    # 2. Explicit stake intent
    if "stake" in q_lower:
        return "stake"

    # 3. Lock BONK is also a stake intent
    if "lock" in q_lower and "bonk" in q_lower:
        return "stake"

    # 4. Static keyword check
    for keyword, intent in STATIC_KEYWORDS.items():
        if keyword in q_lower:
            return "static"

    # 5. Explicit price queries
    if re.search(r"\b(price of|what is the price of)\b", q_lower):
        return "price"

    # 6. Embedding + Pinecone similarity search
    embedding = _model.encode(query).tolist()
    result = index.query(vector=embedding, top_k=1, include_metadata=True)

    if result["matches"]:
        return result["matches"][0]["metadata"]["intent"]

    return None
