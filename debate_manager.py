from typing import List, Dict
from debate_system import DebateAgent
import asyncio
from datetime import datetime

class DebateManager:
    def __init__(self, agent1: DebateAgent, agent2: DebateAgent, topic: str):
        # Ensure the first agent is OpenAI and the second is DeepSeek
        if agent1.name == "OpenAI" and agent2.name == "DeepSeek":
            self.agent1 = agent1  # OpenAI
            self.agent2 = agent2  # DeepSeek
        elif agent2.name == "OpenAI" and agent1.name == "DeepSeek":
            # Swap if they're in the wrong order
            self.agent1 = agent2  # OpenAI
            self.agent2 = agent1  # DeepSeek
            print("Warning: Agents were passed in the wrong order. Swapping to ensure OpenAI is agent1.")
        else:
            # If names don't match, use as passed but warn
            self.agent1 = agent1
            self.agent2 = agent2
            print(f"Warning: Expected agent names 'OpenAI' and 'DeepSeek', but got '{agent1.name}' and '{agent2.name}'")
        
        self.topic = topic
        self.conversation_history: List[Dict] = []
        self.current_turn = 0
        
        # DEBUG: Verify the agent names are correctly assigned
        print(f"DebateManager initialized with agent1={self.agent1.name} and agent2={self.agent2.name}")
        
    async def start_debate(self):
        # Set initial context
        context = f"""
        Scene: {self.topic}
        Participants: {self.agent1.name} vs {self.agent2.name}
        """
        
        # Initial message - OpenAI should always go first
        print(f"Starting debate with first agent: {self.agent1.name}")
        first_response = await self.agent1.generate_response(context, "", self.conversation_history)
        
        # Strictly verify the response is attributed to the correct agent
        self.conversation_history.append({
            "agent": self.agent1.name,
            "message": first_response,
            "timestamp": datetime.now(),
            "agent_identity": "OpenAI"  # Add explicit identity
        })
        
        return first_response

    async def next_turn(self) -> str:
        # Determine which agent's turn it is based on conversation length
        # OpenAI agent should always be on even turns, DeepSeek on odd turns
        
        # Force OpenAI for even turns, DeepSeek for odd
        if len(self.conversation_history) % 2 == 0:
            current_agent = self.agent1  # Should be OpenAI
            opponent_agent = self.agent2  # Should be DeepSeek
            agent_identity = "OpenAI"
        else:
            current_agent = self.agent2  # Should be DeepSeek
            opponent_agent = self.agent1  # Should be OpenAI
            agent_identity = "DeepSeek"
        
        # Double-check the name matches the expected identity
        if current_agent.name != agent_identity:
            print(f"ERROR: Agent mismatch! Expected {agent_identity} but got {current_agent.name}")
            # Force correct assignment
            current_agent = self.agent1 if agent_identity == "OpenAI" else self.agent2
        
        # CRITICAL DEBUG: Print which agent is currently speaking
        print(f"CURRENT TURN: {current_agent.name} (turn #{len(self.conversation_history)})")
        
        # Get last message as the opponent message
        opponent_message = self.conversation_history[-1]["message"]
        context = self._build_context()
        
        # Generate response with explicitly named agent
        print(f"Generating response for {current_agent.name}")
        response = await current_agent.generate_response(context, opponent_message, self.conversation_history)
        print(f"Response generated for {current_agent.name}: {response[:30]}...")
        
        # Store with explicit identity tag
        self.conversation_history.append({
            "agent": current_agent.name,
            "message": response,
            "timestamp": datetime.now(),
            "agent_identity": agent_identity  # Track explicit identity
        })
        
        self.current_turn += 1
        return response

    def _build_context(self) -> str:
        return "\n".join([f"{msg['agent']}: {msg['message']}" 
                         for msg in self.conversation_history[-3:]]) 