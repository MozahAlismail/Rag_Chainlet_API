import chainlit as cl
import httpx
import os

# Use environment variable for API URL, fallback to localhost for development
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/chat")

@cl.on_message
async def handle_message(message: cl.Message):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Try the new API format first
            response = await client.post(FASTAPI_URL, json={"question": message.content})
            
            if response.status_code == 200:
                data = response.json()
                if "answer" in data:
                    answer = data["answer"]
                elif "error" in data:
                    answer = f"❌ API Error: {data['error']}"
                else:
                    answer = f"❌ Unexpected response format: {data}"
            elif response.status_code == 422:
                # Try legacy format
                legacy_url = FASTAPI_URL.replace("/chat", "/chat-legacy")
                response = await client.post(legacy_url, json={"question": message.content})
                data = response.json()
                answer = data.get("answer", data.get("error", "Unknown error"))
            else:
                answer = f"❌ API Error: {response.status_code} - {response.text}"
                
    except httpx.ConnectError:
        answer = f"❌ Connection Error: Cannot connect to FastAPI server at {FASTAPI_URL}\n\nPlease ensure:\n1. FastAPI server is running\n2. Server is accessible at {FASTAPI_URL}\n3. No firewall is blocking the connection"
    except httpx.TimeoutException:
        answer = "⏱️ Timeout Error: The API server took too long to respond (>60s). The model might be loading for the first time."
    except Exception as e:
        answer = f"🔥 Unexpected Error: {str(e)}"
    
    await cl.Message(content=answer).send()