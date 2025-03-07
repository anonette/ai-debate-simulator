import os
import requests
from typing import List
import json
from datetime import datetime
import sys

class ModelDebate:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_base = "https://openrouter.ai/api/v1/chat/completions"
        
        self.debate_prompt = """
Debate topic:
Should AI be open infrastructure or controlled by a few corporations?

Previous point: {previous_point}
"""

    def get_model_response(self, previous_point: str, model: str) -> str:
        """Get response from specified model via OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }
        
        prompt = self.debate_prompt.format(previous_point=previous_point)
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.api_base, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error getting response: {str(e)}"

    def conduct_debate(self, rounds: int = 3) -> List[str]:
        """Conduct a debate between the models"""
        transcript = []
        
        title = "Debate"
        round_text = "Round"
        
        header = f"\n{'='*80}\n{title}\n{'='*80}\n"
        print(header, flush=True)
        transcript.append(header)
        
        model1 = "google/gemini-pro"
        model2 = "google/gemini-pro"
        
        previous_point = ""
        
        for round_num in range(rounds):
            round_header = f"{round_text} {round_num + 1}\n{'-'*40}"
            print(round_header, flush=True)
            transcript.append(round_header)
            
            # First agent response
            print(f"Waiting for Gemini-1...", end='\r', flush=True)
            gemini1_response = self.get_model_response(previous_point, model1)
            timestamp = datetime.now().strftime("%H:%M:%S")
            response_text = f"[{timestamp}] Gemini-1:\n  {gemini1_response}\n"
            print(" " * 50, end='\r')  # Clear the waiting message
            print(response_text, flush=True)
            transcript.append(response_text)
            previous_point = gemini1_response
            
            # Second agent response
            print(f"Waiting for Gemini-2...", end='\r', flush=True)
            gemini2_response = self.get_model_response(previous_point, model2)
            timestamp = datetime.now().strftime("%H:%M:%S")
            response_text = f"[{timestamp}] Gemini-2:\n  {gemini2_response}\n"
            print(" " * 50, end='\r')  # Clear the waiting message
            print(response_text, flush=True)
            transcript.append(response_text)
            previous_point = gemini2_response
            
        footer = "="*80
        print(footer, flush=True)
        transcript.append(footer)
        return transcript

def main():
    debate = ModelDebate()
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Prepare log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(logs_dir, f"debate_english_{timestamp}.txt")
    
    # Stream debate and log simultaneously
    with open(filename, 'w', encoding='utf-8') as f:
        transcript = []
        for line in debate.conduct_debate(rounds=4):
            f.write(line + '\n')
            f.flush()  # Ensure immediate write to file
            transcript.append(line)
    
    print(f"\nDebate transcript saved to: {filename}")

if __name__ == "__main__":
    main() 