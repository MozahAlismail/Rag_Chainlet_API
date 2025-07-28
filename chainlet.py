import chainlit as cl
import httpx
import os
import asyncio
import subprocess
import time
import sys
import threading
import uvicorn
from multiprocessing import Process
import signal
import atexit

# Configuration - Dynamic based on environment
def get_environment_config():
    """Get configuration based on deployment environment"""
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    is_production = os.getenv("HUGGINGFACE_API_TOKEN") is not None or is_railway
    
    if is_railway:
        # Railway deployment
        host = "0.0.0.0"
        port = int(os.getenv("PORT", 8000))
        api_url = os.getenv("FASTAPI_URL", f"http://0.0.0.0:{port}/chat")
        chainlit_port = port  # Use same port for Railway
        return host, port, chainlit_port, api_url, "Railway"
    elif is_production:
        # Other production environment
        host = "0.0.0.0"
        api_port = 8000
        chainlit_port = 8001
        api_url = os.getenv("FASTAPI_URL", f"http://0.0.0.0:{api_port}/chat")
        return host, api_port, chainlit_port, api_url, "Production"
    else:
        # Local development
        host = "127.0.0.1"
        api_port = 8000
        chainlit_port = 8001
        api_url = os.getenv("FASTAPI_URL", f"http://localhost:{api_port}/chat")
        return host, api_port, chainlit_port, api_url, "Development"

# Get dynamic configuration
FASTAPI_HOST, FASTAPI_PORT, CHAINLIT_PORT, FASTAPI_URL, ENVIRONMENT_TYPE = get_environment_config()

# Global variables for server management
api_server_process = None
api_server_thread = None

def check_api_server():
    """Check if the API server is running"""
    try:
        import requests
        response = requests.get(f"http://{FASTAPI_HOST}:{FASTAPI_PORT}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the FastAPI server in a separate process"""
    global api_server_process
    
    # Skip starting API server in Railway since it's managed separately
    if ENVIRONMENT_TYPE == "Railway":
        print("🚂 Railway environment - API server managed by platform")
        return True
    
    if check_api_server():
        print("✅ API server already running")
        return True
    
    print("🚀 Starting FastAPI server...")
    
    try:
        # Import and start the FastAPI app
        from api import app
        
        def run_server():
            uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT, log_level="info")
        
        # Start server in a separate thread
        global api_server_thread
        api_server_thread = threading.Thread(target=run_server, daemon=True)
        api_server_thread.start()
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            if check_api_server():
                print("✅ FastAPI server started successfully")
                return True
            time.sleep(1)
            print(f"⏳ Waiting for API server to start... ({i+1}/30)")
        
        print("❌ Failed to start API server within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return False

def stop_api_server():
    """Stop the API server"""
    global api_server_process, api_server_thread
    
    if api_server_process:
        api_server_process.terminate()
        api_server_process = None
        print("🛑 API server process terminated")
    
    if api_server_thread:
        # Thread will be cleaned up automatically since it's a daemon thread
        api_server_thread = None
        print("🛑 API server thread stopped")

# Register cleanup function
atexit.register(stop_api_server)

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    # Different behavior based on environment
    if ENVIRONMENT_TYPE == "Railway":
        # In Railway, the API is part of the same service
        await cl.Message(
            content="🎉 **Welcome to the AI Policy Assistant!**\n\n"
                    "🚂 **Railway Deployment**\n"
                    "✅ Integrated API and chat interface\n"
                    "✅ RAG system is ready\n\n"
                    "Ask me anything about AI governance, policies, or data management!"
        ).send()
    else:
        # Local development - start API server if not running
        if not check_api_server():
            print("🔄 API server not detected, starting...")
            if start_api_server():
                await cl.Message(
                    content="🎉 **Welcome to the AI Policy Assistant!**\n\n"
                            "✅ Backend API server is running\n"
                            "✅ RAG system is ready\n\n"
                            "Ask me anything about AI governance, policies, or data management!"
                ).send()
            else:
                await cl.Message(
                    content="⚠️ **Warning: Backend API server failed to start**\n\n"
                            "The chat interface is ready, but the AI backend may not be available.\n"
                            "Please check the console for error messages."
                ).send()
        else:
            await cl.Message(
                content="🎉 **Welcome to the AI Policy Assistant!**\n\n"
                        "✅ Connected to running backend API\n"
                        "✅ RAG system is ready\n\n"
                        "Ask me anything about AI governance, policies, or data management!"
            ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming messages"""
    # Show loading message
    loading_msg = cl.Message(content="🤔 Thinking...")
    await loading_msg.send()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout for model loading
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
        answer = (f"❌ **Connection Error**\n\n"
                 f"Cannot connect to the API server at {FASTAPI_URL}\n\n"
                 f"**Troubleshooting:**\n"
                 f"1. API server may be starting up (please wait)\n"
                 f"2. Check if the server is accessible at {FASTAPI_URL}\n"
                 f"3. Verify no firewall is blocking the connection\n\n"
                 f"*The API server should start automatically. Please try again in a few seconds.*")
    except httpx.TimeoutException:
        answer = ("⏱️ **Timeout Error**\n\n"
                 "The API server took too long to respond (>120s).\n"
                 "This usually happens when the AI model is loading for the first time.\n\n"
                 "**Please try again** - subsequent requests should be faster.")
    except Exception as e:
        answer = f"🔥 **Unexpected Error**\n\n{str(e)}\n\nPlease try again or contact support if the issue persists."
    
    # Update the loading message with the response
    await loading_msg.update(content=answer)

def main():
    """Main function to start the complete system"""
    print("=" * 60)
    print("🚀 RAG CHAINLIT API - MAIN LAUNCHER")
    print("=" * 60)
    
    print(f"🔧 Configuration:")
    print(f"   Environment Type: {ENVIRONMENT_TYPE}")
    print(f"   FastAPI URL: {FASTAPI_URL}")
    print(f"   FastAPI Host: {FASTAPI_HOST}:{FASTAPI_PORT}")
    print(f"   Chainlit Port: {CHAINLIT_PORT}")
    print(f"   Railway Environment: {'Yes' if os.getenv('RAILWAY_ENVIRONMENT') else 'No'}")
    print(f"   HuggingFace Token: {'Set' if os.getenv('HUGGINGFACE_API_TOKEN') else 'Not Set'}")
    print()
    
    # Environment-specific startup logic
    if ENVIRONMENT_TYPE == "Railway":
        print("🚂 Railway deployment detected")
        print("   - API and Chainlit will run on the same port")
        print("   - Platform will manage the API server")
        print("   - Using 0.0.0.0 host for external access")
    elif ENVIRONMENT_TYPE == "Production":
        print("🌐 Production environment detected")
        print("   - Will manage API server automatically")
        print("   - Using 0.0.0.0 host for external access")
        print("   - API and Chainlit on separate ports")
        
        # Pre-start API server for faster first response
        if start_api_server():
            print("✅ API server pre-started successfully")
        else:
            print("⚠️  API server will be started when needed")
    else:
        print("💻 Local development mode")
        print("   - Will manage API server automatically")
        print("   - Using localhost (127.0.0.1) for local access")
        print("   - API and Chainlit on separate ports")
        
        # Pre-start API server for faster first response
        if start_api_server():
            print("✅ API server pre-started successfully")
        else:
            print("⚠️  API server will be started when needed")
    
    print()
    print(f"🌐 Starting Chainlit interface on {FASTAPI_HOST}:{CHAINLIT_PORT}...")
    print("=" * 60)

if __name__ == "__main__":
    main()