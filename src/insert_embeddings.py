# src/insert_embeddings.py

import sys, os, json
from pathlib import Path

# Make sure "src" is on sys.path so absolute imports always work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.intent_recognition import index
from src.embeddings import generate_embedding


def upsert_intents(filepath: str = "upsert.json"):
    """
    Load training examples from a JSON file and insert them into Pinecone.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Intent file {filepath} not found.")
    
    with open(path, "r") as f:
        intents = json.load(f)

    vectors = []
    for intent, examples in intents.items():
        for i, example in enumerate(examples):
            embedding = generate_embedding(example)
            vectors.append((f"{intent}_{i}", embedding, {"intent": intent}))

    if vectors:
        index.upsert(vectors=vectors)


def main():
    print("Starting upsert...")
    upsert_intents()
    print("Intents have been upserted into Pinecone!")


if __name__ == "__main__":
    main()
