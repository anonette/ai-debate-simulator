import json
import random
from dotenv import load_dotenv
import os
import httpx
from datetime import datetime

class DebateAgent:
    def __init__(self, agent_config, api_key=None):
        # Load environment variables
        load_dotenv()
        
        # Support both direct name/personality and config dict initialization
        if isinstance(agent_config, dict):
            self.name = agent_config.get('name', '')
            self.model = agent_config.get('model', '')
            self.personality = "luxury chef" if self.name == "OpenAI" else "street food vendor"
        else:
            self.name = agent_config
            self.personality = api_key
            api_key = None
            self.model = "openai/gpt-4o" if self.name == "OpenAI" else "deepseek/deepseek-chat-v3-0324"
        
        self.conversation_data = self.load_conversation()
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        
    def load_conversation(self):
        try:
            # Try to open file from the logs/ai_war directory
            conversation_path = 'logs/ai_war/debate_conversation.json'
            # Open file with UTF-8 encoding
            with open(conversation_path, 'r', encoding='utf-8') as f:
                return [msg for msg in json.load(f) if msg['agent'] == self.name]
        except UnicodeDecodeError:
            # Fallback to different encoding if UTF-8 fails
            with open(conversation_path, 'r', encoding='utf-8-sig') as f:
                return [msg for msg in json.load(f) if msg['agent'] == self.name]
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []
            
    async def generate_response(self, context: str, last_message: str) -> str:
        # Check if we have valid API key
        if not self.api_key:
            print(f"Warning: No API key found for {self.name}. Using fallback response.")
            return f"{self.name} ({self.personality}): This is a placeholder response."
        
        # Create the prompt for the AI model
        prompt = self._create_prompt(context, last_message)
        
        try:
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8501",  # For OpenRouter attribution
                "Content-Type": "application/json"
            }
            
            # Use the appropriate model based on agent name
            model = self.model if hasattr(self, 'model') and self.model else \
                   ("openai/gpt-4o" if self.name == "OpenAI" else "deepseek/deepseek-chat-v3-0324")
            
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are {self.name}, a {self.personality} in a metaphorical debate about AI development. "
                                  f"Use cooking metaphors that reflect your approach to AI. "
                                  f"For OpenAI: emphasize high-quality, resource-intensive approaches. "
                                  f"For DeepSeek: emphasize efficiency and doing more with less."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Print debug information about the request
            print(f"Sending request to OpenRouter API with model: {model}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    # Save this response to the conversation file
                    self._save_response(ai_response, last_message)
                    return ai_response
                else:
                    print(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error generating response: {type(e).__name__}: {str(e)}")
        
        # Fallback to existing conversation data if API call fails
        if self.conversation_data:
            return random.choice(self.conversation_data)['message']
        return f"{self.name} ({self.personality}): This is a placeholder response."
            
    def _create_prompt(self, context: str, last_message: str) -> str:
        """Create a prompt for the AI model based on context and last message"""
        return f"""
Debate context: AI model training approaches
Previous messages: {context}

Last message from opponent: {last_message}

Respond as {self.name}, a {self.personality}, using cooking metaphors to describe your AI development approach. 
Make your response creative, witty, and include subtle jabs at your opponent's approach.
Write your response in this format:
*[cooking action]* 

[Your metaphorical statement about AI development]
"""
    
    def _save_response(self, response: str, last_message: str):
        """Save generated response to conversation history file"""
        try:
            # Ensure the logs/ai_war directory exists
            os.makedirs("logs/ai_war", exist_ok=True)
            
            # Get existing conversation or create new one
            conversation_path = 'logs/ai_war/debate_conversation.json'
            try:
                with open(conversation_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                conversation = []
            
            # Add new response
            conversation.append({
                "agent": self.name,
                "message": response,
                "recipient": "OpenAI" if self.name == "DeepSeek" else "DeepSeek",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Save updated conversation
            with open(conversation_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2)
                
            # Update the agent's conversation data
            self.conversation_data = [msg for msg in conversation if msg['agent'] == self.name]
            
        except Exception as e:
            print(f"Error saving response: {e}")