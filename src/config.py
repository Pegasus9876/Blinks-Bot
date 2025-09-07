# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Pinecone credentials
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "blinkbot")

# HuggingFace embedding model (for generating vectors)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
