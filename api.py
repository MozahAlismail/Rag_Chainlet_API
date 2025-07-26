from fastapi import FastAPI, Request
import uvicorn
import nest_asyncio
from rag import rag_chat


app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "RAG Chainlit API"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    question = data["question"]

    answer = rag_chat(question)

    return {"answer": answer}