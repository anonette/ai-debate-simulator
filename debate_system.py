import json
import random
from dotenv import load_dotenv
import os

class DebateAgent:
    def __init__(self, name: str, personality: str):
        # Load environment variables
        load_dotenv()
        
        self.name = name
        self.personality = personality
        self.conversation_data = self.load_conversation()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
    def load_conversation(self):
        try:
            # Open file with UTF-8 encoding
            with open('debate_conversation.json', 'r', encoding='utf-8') as f:
                return [msg for msg in json.load(f) if msg['agent'] == self.name]
        except UnicodeDecodeError:
            # Fallback to different encoding if UTF-8 fails
            with open('debate_conversation.json', 'r', encoding='utf-8-sig') as f:
                return [msg for msg in json.load(f) if msg['agent'] == self.name]
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []
        
    async def generate_response(self, context: str, last_message: str) -> str:
        # Get a random message from this agent's conversation history
        if self.conversation_data:
            return random.choice(self.conversation_data)['message']
        return f"{self.name} ({self.personality}): This is a placeholder response." 