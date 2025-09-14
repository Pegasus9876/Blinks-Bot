from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-mpnet-base-v2")

def generate_embedding(text: str) -> list:
    """
    Generate an embedding vector for a given text.
    Args:
        text (str): Input text query or training example.
    Returns:
        list: Embedding as a list of floats.
    """
    return _model.encode(text.lower()).tolist()
