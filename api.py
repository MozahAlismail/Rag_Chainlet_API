from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import nest_asyncio
import os
import traceback

# Define request model for better validation
class ChatRequest(BaseModel):
    question: str

# Initialize the RAG function with proper error handling
rag_chat = None
rag_initialized = False

def initialize_rag():
    """Initialize RAG system on first request"""
    global rag_chat, rag_initialized
    
    if rag_initialized:
        return True
    
    try:
        # Use optimized RAG for production, fallback to original for development
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HUGGINGFACE_API_TOKEN"):
            print("Loading optimized RAG implementation...")
            from rag_optimized import rag_chat, initialize_rag_system
            print("✅ Optimized RAG loaded successfully")
            
            # Initialize the system
            if hasattr(locals().get('initialize_rag_system'), '__call__'):
                initialize_rag_system()
        else:
            print("Loading original RAG implementation...")
            from rag import rag_chat, initialize_rag_system
            print("✅ Original RAG loaded successfully")
            
            # Initialize the system
            initialize_rag_system()
            
        rag_initialized = True
        return True
        
    except Exception as e:
        print(f"❌ Error loading RAG implementation: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

try:
    # Try to import and initialize on startup (for faster first response)
    initialize_rag()
except Exception as e:
    print(f"⚠️  Could not initialize RAG on startup: {e}")
    print("RAG will be initialized on first request.")

app = FastAPI(title="RAG Chainlit API", description="AI Policy Assistant API")

@app.get("/")
async def health_check():
    return {
        "status": "healthy", 
        "service": "RAG Chainlit API", 
        "version": "1.0.0",
        "rag_loaded": rag_chat is not None,
        "rag_initialized": rag_initialized,
        "environment": "production" if (os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HUGGINGFACE_API_TOKEN")) else "development"
    }

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        # Initialize RAG if not already done
        if not rag_initialized:
            print("🔄 Initializing RAG system on first request...")
            if not initialize_rag():
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to initialize RAG system. Check server logs."
                )
        
        # Check if RAG is properly loaded
        if rag_chat is None:
            raise HTTPException(
                status_code=500, 
                detail="RAG system not properly initialized. Check server logs for import errors."
            )
        
        question = chat_request.question.strip()
        
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"Processing question: {question}")
        
        # Call the RAG function
        answer = rag_chat(question)
        
        if not answer:
            answer = "I apologize, but I couldn't generate a response. Please try again."
        
        print(f"Generated answer: {answer[:100]}...")
        
        return {"answer": answer}
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

# Alternative endpoint for backwards compatibility
@app.post("/chat-legacy")
async def chat_legacy(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "").strip()
        
        if not question:
            return {"error": "Question cannot be empty"}
        
        if rag_chat is None:
            return {"error": "RAG system not properly initialized"}
        
        answer = rag_chat(question)
        return {"answer": answer or "No response generated"}
    
    except Exception as e:
        print(f"❌ Error in legacy chat endpoint: {e}")
        return {"error": f"Error processing request: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)