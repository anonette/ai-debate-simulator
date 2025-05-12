import json
import random
from dotenv import load_dotenv
import os
import yaml
import requests
import asyncio

class DebateAgent:
    def __init__(self, name: str, personality: str):
        # Load environment variables
        load_dotenv()
        
        self.name = name
        self.personality = personality
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Load debate configuration
        self.config = self.load_config()
        
        # Debug
        print(f"Initialized agent: {self.name} with personality type: {personality[:20]}...")
        
    def load_config(self):
        try:
            with open('config.yaml', 'r') as file:
                return yaml.safe_load(file)
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
        
    async def generate_response(self, context: str, opponent_message: str, conversation_history=None) -> str:
        # If we're in test mode or don't have an API key, return a placeholder response
        if not self.api_key:
            print("No API key found - using placeholder response")
            return self.generate_placeholder_response()
        
        # For debugging
        print(f"Generating response for agent: {self.name}")
        
        # Find the right agent configuration
        agent_config = None
        if self.name == "OpenAI":
            agent_config = self.config.get('agents', {}).get('openai', {})
            model = agent_config.get('model', "openai/gpt-4-turbo-preview") 
        elif self.name == "DeepSeek":
            agent_config = self.config.get('agents', {}).get('deepseek', {})
            model = agent_config.get('model', "deepseek/deepseek-chat")
            
        if not agent_config:
            print("No agent config found - using placeholder response")
            return self.generate_placeholder_response()
        
        # Get the debate prompt
        debate_prompt = self.config.get('debate_prompt', '')
        
        # Build the prompt by filling in the template with actual values
        personality = agent_config.get('personality', '')
        prompt = f"{personality}\n\n{debate_prompt}".format(
            name=self.name, 
            opponent_message=opponent_message
        )
        
        print(f"Calling API for {self.name} using model: {model}")
        
        # Make the API call to OpenRouter
        try:
            response = await self.call_openrouter_api(prompt, model)
            if response:
                return response
            else:
                print("API call failed - using placeholder response")
                return self.generate_placeholder_response()
        except Exception as e:
            print(f"Error calling API: {e}")
            return self.generate_placeholder_response()
        
    async def call_openrouter_api(self, prompt, model):
        """Make an API call to OpenRouter to generate a response"""
        
        # OpenRouter API endpoint
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://kitchendebate.example.com"  # Replace with your actual site
        }
        
        # Request body
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are participating in a debate as a chef. The debate is about AI development approaches."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 150
        }
        
        print(f"Sending request to OpenRouter for {self.name}")
        
        # Make the API call asynchronously
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(api_url, headers=headers, json=data)
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                generated_text = response_data['choices'][0]['message']['content']
                print(f"API response for {self.name}: {generated_text[:50]}...")
                return generated_text
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error in API call: {str(e)}")
            return None
    
    def generate_placeholder_response(self):
        """Generate a placeholder response if API call fails"""
        
        # Basic placeholder responses that match the personalities
        if self.name == "OpenAI":
            actions = [
                "*swirls wine glass while checking GPU cluster metrics*",
                "*adjusts the temperature of a sous-vide bag*",
                "*delicately plates a dish with tweezers*"
            ]
            
            responses = [
                "Our approach to AI is like fine dining - it costs more, but the quality speaks for itself.",
                "Just as a great chef needs the finest ingredients, our models need premium compute resources.",
                "While others rush their models, we slow-cook ours to perfection."
            ]
        else:  # DeepSeek
            actions = [
                "*efficiently stir-fries ingredients with minimal waste*",
                "*skillfully flips a wok with perfect technique*",
                "*serves a delicious dish made with simple ingredients*"
            ]
            
            responses = [
                "Great AI is like great street food - it's about skill and efficiency, not expensive ingredients.",
                "Our models prove you don't need a billion-dollar kitchen to cook up state-of-the-art results.",
                "The best chefs can create masterpieces with limited resources - that's what we do with our models."
            ]
            
        # Select random action and response
        action = random.choice(actions)
        response = random.choice(responses)
        
        return f"{action}\n\"{response}\"" 