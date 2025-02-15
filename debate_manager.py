from typing import List, Dict
from debate_system import DebateAgent
import asyncio
from datetime import datetime

class DebateManager:
    def __init__(self, agent1: DebateAgent, agent2: DebateAgent, topic: str):
        self.agent1 = agent1
        self.agent2 = agent2
        self.topic = topic
        self.conversation_history: List[Dict] = []
        self.current_turn = 0
        
    async def start_debate(self):
        # Set initial context
        context = f"""
        Scene: {self.topic}
        Participants: {self.agent1.name} vs {self.agent2.name}
        """
        
        # Initial message
        first_response = await self.agent1.generate_response(context, "")
        self.conversation_history.append({
            "agent": self.agent1.name,
            "message": first_response,
            "timestamp": datetime.now()
        })
        
        return first_response

    async def next_turn(self) -> str:
        current_agent = self.agent1 if self.current_turn % 2 == 0 else self.agent2
        opponent_agent = self.agent2 if self.current_turn % 2 == 0 else self.agent1
        
        last_message = self.conversation_history[-1]["message"]
        context = self._build_context()
        
        response = await current_agent.generate_response(context, last_message)
        
        self.conversation_history.append({
            "agent": current_agent.name,
            "message": response,
            "timestamp": datetime.now()
        })
        
        self.current_turn += 1
        return response

    def _build_context(self) -> str:
        return "\n".join([f"{msg['agent']}: {msg['message']}" 
                         for msg in self.conversation_history[-3:]]) 