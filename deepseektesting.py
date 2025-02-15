import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek():
    """
    Test DeepSeek-R1 model's reasoning capabilities through OpenRouter
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please show your complete reasoning process."
            },
            {
                "role": "user",
                "content": "Think of a random number."
            }
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
            
            full_content = ""
            full_reasoning = ""
            
            for chunk in response.iter_lines():
                if chunk.startswith("data: "):
                    chunk_data = json.loads(chunk[6:])
                    if "choices" in chunk_data:
                        delta = chunk_data["choices"][0]["delta"]
                        if "content" in delta and delta["content"]:
                            content = delta["content"]
                            print(content, end='', flush=True)
                            full_content += content
                        if "reasoning" in delta and delta["reasoning"]:
                            reasoning = delta["reasoning"]
                            print("\033[34m" + reasoning + "\033[0m", end='', flush=True)
                            full_reasoning += reasoning

            print("\n\nReasoning:", full_reasoning)
            print("\nFull Response:", full_content)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_deepseek()