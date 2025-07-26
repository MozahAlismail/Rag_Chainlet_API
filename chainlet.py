import chainlit as cl
import httpx
import os

# Use environment variable for API URL, fallback to localhost for development
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/chat")

@cl.on_message
async def handle_message(message: cl.Message):
    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL, json={"question": message.content})
        answer = response.json().get("answer", "No answer received.")
    
    await cl.Message(content=answer).send()