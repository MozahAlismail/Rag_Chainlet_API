from fastapi import FastAPI, Request
import uvicorn
import nest_asyncio
import os

# Use optimized RAG for production, fallback to original for development
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HUGGINGFACE_API_TOKEN"):
    from rag_optimized import rag_chat
else:
    from rag import rag_chat


app = FastAPI(title="RAG Chainlit API", description="AI Policy Assistant API")

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "RAG Chainlit API", "version": "1.0.0"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "")
        
        if not question.strip():
            return {"error": "Question cannot be empty"}
        
        answer = rag_chat(question)
        return {"answer": answer}
    
    except Exception as e:
        return {"error": f"Error processing request: {str(e)}"}