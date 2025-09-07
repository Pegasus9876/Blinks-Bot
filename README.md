# BlinkBot – Natural Language → Solana Blinks

This project converts natural language queries into structured Solana Blinks. Funded by a grant from Dialect x Solana.

blink-bot/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── embeddings.py
│   ├── intent_recognition.py
│   ├── parameter_extractors.py
│   ├── processor.py
│   └── tests/
│       ├── __init__.py
│       └── test_processor.py
├── notebooks/
│   └── experiments.ipynb
├── pinecone_index/
├── .gitignore
├── .env.example
├── requirements.txt
├── README.md
├── LICENSE
└── main.py

Input: User says “swap 10 usdc to sol”

Step 1: Check static → no match.

Step 2: Embed + Pinecone → “swap” intent.

Step 3: Run parse_swap_intent(text) → structured JSON.

Step 4: Bot returns Blink link.