import os
import httpx
import json
from dotenv import load_dotenv

async def test_connection():
    """
    Test OpenRouter API connection and configuration
    """
    # Force reload environment variables
    load_dotenv(override=True)
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("Error: No API key found in .env file")
        return
    
    # Debug environment
    print("\nEnvironment Debug:")
    print(f"Working directory: {os.getcwd()}")
    print(f"API Key format: {api_key[:10]}...{api_key[-4:]}")
    print(f"API Key length: {len(api_key)}")
    print(f"Starts with 'sk-or-v1-': {api_key.startswith('sk-or-v1-')}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello, testing the connection!'"
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            result = response.json()
            print("\nSuccess! Response:", result["choices"][0]["message"]["content"])
            
    except Exception as e:
        print("\nError occurred:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection()) 