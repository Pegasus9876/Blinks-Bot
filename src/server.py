from fastapi import FastAPI, Query
from pydantic import BaseModel
from src.intent_recognition import classify_intent
from src.entities import parse_intent

app = FastAPI(title="Blink Bot API")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Blink Bot API is running "}

@app.post("/process")
def process_query(request: QueryRequest):
    query = request.query
    intent = classify_intent(query)
    result = parse_intent(intent, query) if intent else {"error": "Could not classify intent"}
    return {
        "query": query,
        "intent": intent,
        "result": result
    }
