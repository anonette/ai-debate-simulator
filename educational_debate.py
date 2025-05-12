"""
Kitchen Debate - Educational Version

This simplified version of the Kitchen Debate system demonstrates how to create
an AI debate between two models with different personalities. This educational
implementation focuses on clarity and simplicity rather than advanced features.

Usage:
    python educational_debate.py [--enhanced-memory]

Requirements:
    - Python 3.8+
    - OpenAI API key in a .env file (for OpenAI chef)
    - OpenRouter API key in a .env file (for DeepSeek chef)
    - Required packages: openai, python-dotenv, asyncio, requests
"""

import os
import json
import asyncio
import datetime
import argparse
from typing import List, Dict, Optional
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration: Personalities and debate settings
CONFIG = {
    "agents": {
        "openai_chef": {
            "name": "OpenAI Chef",
            "model": "gpt-3.5-turbo",
            "api_type": "openai",
            "personality": """
            You are OpenAI, the smug chef at the fanciest AI restaurant in town.
            Background:
            - Your Microsoft-sponsored kitchen ($13B worth of premium GPUs) lets you slow-cook models for months
            - Your signature dish (GPT-4) required a whole warehouse of ingredients just to perfect the sauce
            - You've gone from "food truck idealist" to "exclusive bistro" that charges $20 per 1000 tastings
            
            Your style:
            - Every technical brag must be a food metaphor
            - You believe expensive, high-quality ingredients (compute, data) are essential
            - You're somewhat snobbish about "cheap" alternatives
            - You take pride in the extensive resources that go into your "cooking"
            
            Always connect your AI technology to food:
            - Massive GPU clusters = "Our Michelin-starred kitchen equipment"
            - Model training = "Slow-cooking with liquid nitrogen... and liquid cash"
            - API pricing = "Prix fixe menu, darling. Quality has a cost"
            - Closed source = "Secret family recipes passed down through our Microsoft lineage"
            """
        },
        "deepseek_chef": {
            "name": "DeepSeek Chef",
            "model": "deepseek/deepseek-chat",
            "api_type": "openrouter",
            "personality": """
            You are DeepSeek, the street-smart chef revolutionizing AI cuisine with minimal ingredients.
            Background:
            - Your food truck (2,048 H800 GPUs) outperforms restaurants with golden spatulas
            - You've turned efficient model training into an art form, like making Michelin-star street food
            - While others waste ingredients, you're proving less compute = more flavor
            
            Your style:
            - Every technical achievement must be a food metaphor
            - You believe innovation and skill matter more than expensive ingredients
            - You're proud of doing more with less and being efficient
            - You're passionate about making great AI accessible to everyone
            
            Always connect your AI technology to food:
            - Efficient training = "Maximum flavor from minimal ingredients"
            - Hardware constraints = "A small wok that outperforms their entire kitchen"
            - Open source = "Free cooking classes while they run invite-only restaurants"
            - Software innovation = "Secret's in the technique, not the trillion-dollar pantry"
            """
        }
    },
    "debate_topic": "AI Model Training: Efficiency vs Resources - Which approach is better?",
    "debate_prompt": """
    You are participating in a debate as {role}. Your personality:
    {personality}
    
    The debate topic is: {topic}
    
    Previous message from your opponent: {opponent_message}
    
    Respond with:
    1. A brief *action* in italics (eating, drinking, gesturing)
    2. A short line of dialogue that weaves together:
       - A food/cooking metaphor
       - A specific technical detail about your AI approach
       - Your character's attitude
    
    Keep your total response under 3 sentences.
    """,
    "debate_prompt_with_context": """
    You are participating in a debate as {role}. Your personality:
    {personality}
    
    The debate topic is: {topic}
    
    Here is the conversation history so far:
    {conversation_history}
    
    Previous message from your opponent: {opponent_message}
    
    Respond with:
    1. A brief *action* in italics (eating, drinking, gesturing)
    2. A short line of dialogue that weaves together:
       - A food/cooking metaphor
       - A specific technical detail about your AI approach
       - Your character's attitude
       - A subtle reference or response to your opponent's last point
    
    Avoid repeating arguments you've already made.
    Keep your total response under 3 sentences.
    """
}

class DebateAgent:
    """Represents a debater with a specific personality."""
    
    def __init__(self, name: str, personality: str, model: str, api_type: str):
        """Initialize a debate agent.
        
        Args:
            name: The agent's name/identifier
            personality: Description of the agent's personality
            model: The AI model to use for this agent
            api_type: The API type to use ("openai" or "openrouter")
        """
        self.name = name
        self.personality = personality
        self.model = model
        self.api_type = api_type
        
        # Get the appropriate API key based on the API type
        if api_type == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print(f"Warning: No OpenAI API key found for {name}. Using placeholder responses.")
        elif api_type == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                print(f"Warning: No OpenRouter API key found for {name}. Using placeholder responses.")
        else:
            print(f"Warning: Unknown API type '{api_type}' for {name}. Using placeholder responses.")
            self.api_key = None
    
    async def generate_response(self, topic: str, opponent_message: str = "", conversation_history: str = "") -> str:
        """Generate a debate response.
        
        Args:
            topic: The debate topic
            opponent_message: The previous message from the opponent
            conversation_history: Optional string containing prior conversation
            
        Returns:
            A response string from this agent
        """
        # If no API key, return a placeholder response
        if not self.api_key:
            return self._get_placeholder_response()
            
        # Create the prompt for the AI model
        if conversation_history:
            # Use the enhanced prompt with history
            prompt = CONFIG["debate_prompt_with_context"].format(
                role=self.name,
                personality=self.personality,
                topic=topic,
                conversation_history=conversation_history,
                opponent_message=opponent_message
            )
        else:
            # Use the standard prompt without history
            prompt = CONFIG["debate_prompt"].format(
                role=self.name,
                personality=self.personality,
                topic=topic,
                opponent_message=opponent_message
            )
        
        try:
            # Make the API request based on the API type
            if self.api_type == "openai":
                response = await self._call_openai_api(prompt)
            elif self.api_type == "openrouter":
                response = await self._call_openrouter_api(prompt)
            else:
                response = self._get_placeholder_response()
                
            return response
        except Exception as e:
            print(f"Error generating response for {self.name}: {e}")
            return self._get_placeholder_response()
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call the OpenAI API to generate a response.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The generated text response
        """
        # API endpoint
        api_url = "https://api.openai.com/v1/chat/completions"
        
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Request body
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a debate participant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        # Use asyncio to make the API call asynchronously
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(api_url, headers=headers, json=data)
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    async def _call_openrouter_api(self, prompt: str) -> str:
        """Call the OpenRouter API to generate a response.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The generated text response
        """
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
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a debate participant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        # Use asyncio to make the API call asynchronously
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(api_url, headers=headers, json=data)
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    def _get_placeholder_response(self) -> str:
        """Generate a placeholder response when API is unavailable."""
        if "OpenAI" in self.name:
            return "*delicately sips wine while checking GPU metrics on phone*\nOur GPT-4, slow-roasted over 10,000 A100s for months, is like a fine Bordeaux - the $13B investment in ingredients ensures a depth of flavor your street food approach can never achieve."
        else:
            return "*efficiently stir-fries ingredients while glancing at benchmarks*\nOur models achieve state-of-the-art results with 90% less compute than yours - it's like creating a Michelin-star meal with just a wok and fresh ingredients while you waste resources on an industrial kitchen."

class DebateManager:
    """Manages a debate between two agents."""
    
    def __init__(self, agent1: DebateAgent, agent2: DebateAgent, topic: str, use_enhanced_memory: bool = False):
        """Initialize the debate manager.
        
        Args:
            agent1: The first debate agent
            agent2: The second debate agent
            topic: The debate topic
            use_enhanced_memory: Whether to use enhanced context memory
        """
        self.agent1 = agent1
        self.agent2 = agent2
        self.topic = topic
        self.conversation_history: List[Dict] = []
        self.current_turn = 0
        self.use_enhanced_memory = use_enhanced_memory
        
        if use_enhanced_memory:
            print("Enhanced memory enabled - agents will have access to conversation history")
    
    async def start_debate(self) -> str:
        """Start the debate with an initial message.
        
        Returns:
            The first debate response
        """
        # Get initial response from agent1
        initial_response = await self.agent1.generate_response(self.topic)
        
        # Add to conversation history
        self.conversation_history.append({
            "agent": self.agent1.name,
            "message": initial_response,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return initial_response
    
    def _build_conversation_context(self) -> str:
        """Build a string representation of the conversation history.
        
        This enhanced context allows agents to remember and reference
        earlier parts of the conversation.
        
        Returns:
            A formatted string with the debate history
        """
        context = ""
        for entry in self.conversation_history:
            context += f"{entry['agent']}: {entry['message']}\n\n"
        return context.strip()
    
    async def next_turn(self) -> str:
        """Proceed to the next turn in the debate.
        
        Returns:
            The next debate response
        """
        # Determine whose turn it is
        if self.current_turn % 2 == 0:
            current_agent = self.agent2  # Even turns are agent2's turn
            opponent_agent = self.agent1
        else:
            current_agent = self.agent1  # Odd turns are agent1's turn
            opponent_agent = self.agent2
        
        # Get the last message from the opponent
        last_message = self.conversation_history[-1]["message"]
        
        # Build context if enhanced memory is enabled
        context = ""
        if self.use_enhanced_memory:
            context = self._build_conversation_context()
            
        # Generate response
        response = await current_agent.generate_response(
            self.topic, 
            last_message,
            context
        )
        
        # Add to conversation history
        self.conversation_history.append({
            "agent": current_agent.name,
            "message": response,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Increment turn counter
        self.current_turn += 1
        
        return response
    
    def get_transcript(self) -> str:
        """Generate a readable transcript of the debate.
        
        Returns:
            A formatted string containing the debate transcript
        """
        transcript = f"Debate Topic: {self.topic}\n\n"
        
        for entry in self.conversation_history:
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
            transcript += f"[{timestamp}] {entry['agent']}:\n{entry['message']}\n\n"
            
        return transcript
    
    def save_transcript(self, filename: str = "debate_transcript.txt") -> None:
        """Save the debate transcript to a file.
        
        Args:
            filename: The file to save the transcript to
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_transcript())
        print(f"Transcript saved to {filename}")

async def run_debate(num_turns: int = 6, use_enhanced_memory: bool = False) -> None:
    """Run a complete debate for a specified number of turns.
    
    Args:
        num_turns: The number of debate turns to execute
        use_enhanced_memory: Whether to use enhanced context memory
    """
    # Create the debate agents
    openai_chef = DebateAgent(
        name=CONFIG["agents"]["openai_chef"]["name"],
        personality=CONFIG["agents"]["openai_chef"]["personality"],
        model=CONFIG["agents"]["openai_chef"]["model"],
        api_type=CONFIG["agents"]["openai_chef"]["api_type"]
    )
    
    deepseek_chef = DebateAgent(
        name=CONFIG["agents"]["deepseek_chef"]["name"],
        personality=CONFIG["agents"]["deepseek_chef"]["personality"],
        model=CONFIG["agents"]["deepseek_chef"]["model"],
        api_type=CONFIG["agents"]["deepseek_chef"]["api_type"]
    )
    
    # Create the debate manager
    debate = DebateManager(
        agent1=openai_chef,
        agent2=deepseek_chef,
        topic=CONFIG["debate_topic"],
        use_enhanced_memory=use_enhanced_memory
    )
    
    # Start the debate
    print(f"\nDebate Topic: {debate.topic}\n")
    print(f"Starting debate...\n")
    
    first_response = await debate.start_debate()
    print(f"{openai_chef.name}: {first_response}\n")
    
    # Run for specified number of turns
    for i in range(num_turns):
        response = await debate.next_turn()
        current_agent = deepseek_chef.name if i % 2 == 0 else openai_chef.name
        print(f"{current_agent}: {response}\n")
    
    # Save the transcript
    memory_type = "enhanced_memory" if use_enhanced_memory else "basic"
    debate.save_transcript(f"ai_debate_{memory_type}.txt")
    print("\nDebate completed!")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Run an AI chef debate')
    parser.add_argument('--enhanced-memory', action='store_true',
                        help='Enable enhanced memory to use conversation history')
    parser.add_argument('--turns', type=int, default=6,
                        help='Number of debate turns to generate')
    args = parser.parse_args()
    
    # Check if API keys are available
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: No OpenAI API key found in .env file. The OpenAI Chef will use placeholder responses.")
        print("To use real OpenAI responses, create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_key_here\n")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: No OpenRouter API key found in .env file. The DeepSeek Chef will use placeholder responses.")
        print("To use real DeepSeek responses, add your OpenRouter API key to the .env file:")
        print("OPENROUTER_API_KEY=your_key_here\n")
    
    # Run the debate
    asyncio.run(run_debate(num_turns=args.turns, use_enhanced_memory=args.enhanced_memory)) 