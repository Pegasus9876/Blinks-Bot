# Blinks-Bot — README

A pragmatic assistant for Solana token actions (swap, price, balance, stake, donate, games, etc.).  
This repo contains a CLI + lightweight intent/entity parsing pipeline and a small HTTP endpoint for integration.

---

## Contents (high level)

* `main.py` — interactive CLI for quick play (type queries, get parsed results / links).
* `src/intent_recognition.py` — intent classifier (static rules + embeddings + Pinecone lookup).
* `src/entities.py` — entity parsers (token extraction, wallet, domain, amount, URL generation).
* `src/token_loader.py` — downloads the Solana token list and writes `data/tokens.json`.
* `data/tokens.json` — cached token symbol list (preloaded for fast lookups).
* `src/tests/test_processor.py` — integration-style tests that run classification + entity parsing.
* `data/upsert.json` — training examples used by the upsert script.
* `tools/upsert_intents.py` — upsert training examples into Pinecone (embedding + index).

---

## Quickstart (local dev)

1. Clone repo and move to project root

   ```bash
   git clone https://github.com/Pegasus9876/Blinks-Bot
   cd blink-bot
   ```

2. Create & activate a venv

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Pinecone API key:  

   Pinecone is a vector database to store and query embeddings.  
   [pinecone.io](https://www.pinecone.io) to create an API key.  

   ```ini
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX_NAME=blinkbot
   ```

5. Refresh token cache (download Solana token list) --> optional

   ```bash
   python src/token_loader.py --refresh
   ```

6. Run CLI

   ```bash
   python main.py
   ```

7. Run tests


   

Try sample queries:  
   - `swap usdc to eth`  
   - `buy bonk`  
   - `buy a keystone wallet`  
   - `can you please swap jup to sol`


   ```bash
   python src/tests/test_processor.py
   ```

---

## Token cache behavior

`src/entities.py` uses a two-level approach to identify token symbols:

1. **Local cache** — `data/tokens.json` (fast lookup). Created/updated via `src/token_loader.py --refresh`.
2. **Lightweight fallback API** — Jupiter lite-search (`https://lite-api.jup.ag/tokens/v2/search?query=`).

Force-refresh the token file: --> not needed

```bash
python src/token_loader.py --refresh
```

--- 

## Upserting intent examples to Pinecone

Script reads `data/upsert.json` and upserts vectors into Pinecone:

```bash
python tools/upsert_intents.py
```

Requirements:

* `src/embeddings.py` must export `generate_embedding(text)`
* Pinecone configured, `src/intent_recognition.py` has `index` object.

---

## API / Integration

Example FastAPI test:

```bash
curl -X POST "http://127.0.0.1:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"query":"stake BONK"}'
```

Start server:

```bash
uvicorn src.server:app --reload
```

---

## Tips & common fixes

* Run tests/scripts from **project root** to avoid `No module named 'src'`
* Token lookups may be slow on first API call; cached after first lookup.

---

## Examples

* `swap 10 usdc to sol` → `https://jup.ag/swap/USDC-SOL?amount=10.0`
* `price of ethereum` → `https://www.coingecko.com/en/coins/ethereum`
* `open Keystone Wallet` → `https://keyst.one/`

---

## File structure

```
Blinks-Bot/
├─ main.py
├─ requirements.txt
├─ src/
│  ├─ intent_recognition.py
│  ├─ entities.py
│  ├─ token_loader.py
│  ├─ embeddings.py
│  ├─ server.py
│  ├─ tests/
│  │  └─ test_processor.py
├─ data/
│  ├─ tokens.json
│  └─ upsert.json
├─ tools/
│  └─ upsert_intents.py
├─ .env.example
└─ README.md
```
<img width="1570" height="3839" alt="Mermaid_Blink-bot" src="https://github.com/user-attachments/assets/10afbb64-7280-4c17-a0a1-24577625dbd3" />

---

## Contributing / Next steps

* Improve token extraction.
* Add confidence scoring to intent recognition.
* Add unit tests for entities.
