import streamlit as st
from debate_manager import DebateManager
from debate_system import DebateAgent
import asyncio
import json
from datetime import datetime
from debate_logger import DebateLogger

class StreamlitDebateManager:
    def __init__(self):
        # Initialize debate agents
        self.agent1 = DebateAgent(name="OpenAI", personality="luxury chef")
        self.agent2 = DebateAgent(name="DeepSeek", personality="street food vendor")
        self.logger = DebateLogger()
        
        # Initialize debate manager
        self.debate = DebateManager(
            agent1=self.agent1,
            agent2=self.agent2,
            topic="AI Model Training: Efficiency vs Resources"
        )
        self.logger.log_event("Debate Initialized", f"Topic: {self.debate.topic}")

    async def get_next_response(self):
        if not self.debate.conversation_history:
            response = await self.debate.start_debate()
            self.logger.log_event("Debate Started", "First turn initiated")
        else:
            response = await self.debate.next_turn()
        return response

def load_conversation_history():
    with open('debate_conversation.json', 'r') as f:
        return json.load(f)

def main():
    st.title("🤖 AI Debate: OpenAI vs DeepSeek")
    
    # Add debate context
    st.markdown("""
    ### Topic: AI Model Training - Efficiency vs Resources
    
    **OpenAI**: *Luxury chef focusing on premium ingredients and extensive resources*
    
    **DeepSeek**: *Street food vendor emphasizing efficiency and minimal resources*
    """)
    
    if 'debate_manager' not in st.session_state:
        st.session_state.debate_manager = StreamlitDebateManager()
    
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Display conversation history with improved formatting
    for message in st.session_state.conversation:
        with st.chat_message(message["agent"], avatar="🎩" if message["agent"] == "OpenAI" else "🍜"):
            st.markdown(f"**{message['agent']}**")
            st.markdown(message["message"])
            st.markdown("---")

    # Control buttons in columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎭 Next Turn", use_container_width=True):
            response = asyncio.run(st.session_state.debate_manager.get_next_response())
            current_agent = st.session_state.debate_manager.debate.agent1.name if len(st.session_state.conversation) % 2 == 0 else st.session_state.debate_manager.debate.agent2.name
            
            st.session_state.conversation.append({
                "agent": current_agent,
                "message": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.rerun()

            # Log the debate turn
            st.session_state.debate_manager.logger.log_debate_turn(current_agent, response)

    with col2:
        if st.button("🔄 Reset Debate", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.debate_manager = StreamlitDebateManager()
            st.rerun()

if __name__ == "__main__":
    main() 