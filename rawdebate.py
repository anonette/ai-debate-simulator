"""AI Debate with Food Metaphors"""
import os, requests
from dotenv import load_dotenv

load_dotenv()

PROMPT = """
You are {role}. Use ONE food metaphor to argue about AI training.
OpenAI: Luxury chef, believes in using massive resources
DeepSeek: Street chef, believes in efficiency

Previous point: {prev}
Respond in under 15 words.
"""

def get_response(is_openai: bool, prev_msg: str) -> str:
    try:
        return requests.post(
            "https://api.openai.com/v1/chat/completions" if is_openai else "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY' if is_openai else 'OPENROUTER_API_KEY')}"},
            json={
                "model": "gpt-4" if is_openai else "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": PROMPT.format(
                    role="OpenAI (luxury chef)" if is_openai else "DeepSeek (street chef)",
                    prev=prev_msg
                )}],
                "temperature": 0.7,
                "max_tokens": 40
            }
        ).json()["choices"][0]["message"]["content"]
    except:
        return "*checking metrics*"

def debate(turns=6):
    messages = []
    prev = "Should AI use massive resources or focus on efficiency?"
    
    for i in range(turns):
        response = get_response(i % 2 == 0, prev)
        chef = "OpenAI" if i % 2 == 0 else "DeepSeek"
        print(f"{chef}: {response}")
        messages.append(f"{chef}: {response}")
        prev = response
    
    with open("debate.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(messages))

if __name__ == "__main__":
    debate() 