import os
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "blinkbot")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
