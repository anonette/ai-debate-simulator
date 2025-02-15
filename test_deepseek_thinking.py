import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_thinking(prompt: str):
    """
    Test O1's thinking responses through OpenRouter with streaming
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "http://localhost:8501",  # For OpenRouter tracking
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/o1-preview",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Show your reasoning step by step."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "include_reasoning": True
    }
    
    try:
        with httpx.stream('POST', 
                         "https://openrouter.ai/api/v1/chat/completions",
                         headers=headers,
                         json=data,
                         timeout=None) as response:
            
            full_response = ""
            for chunk in response.iter_lines():
                if chunk.startswith("data: "):
                    chunk_data = json.loads(chunk[6:])
                    if "choices" in chunk_data:
                        if "reasoning" in chunk_data["choices"][0]["delta"]:
                            reasoning = chunk_data["choices"][0]["delta"]["reasoning"]
                            print("\033[34m" + reasoning + "\033[0m", end='', flush=True)
                            full_response += f"<think>{reasoning}</think>"
                        if "content" in chunk_data["choices"][0]["delta"]:
                            content = chunk_data["choices"][0]["delta"]["content"]
                            print("\033[32m" + content + "\033[0m", end='', flush=True)
                            full_response += content

            return f"\n\nFull Response:\n{full_response}"
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    test_prompts = [
        "What is deixis?",
        "Explain how a quantum computer works",
        "Why is the sky blue?"
    ]
    
    for prompt in test_prompts:
        print(f"\n=== Testing prompt: {prompt} ===\n")
        response = test_deepseek_thinking(prompt)
        print(response)
        print("\n" + "="*50) 