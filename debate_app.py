# This is the main file you should use
import streamlit as st
from debate_manager import DebateManager
from debate_system_fixed import DebateAgent  # Updated to use the fixed version
import asyncio
import json
import yaml
import os
from datetime import datetime
from debate_logger import DebateLogger

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"Failed to load configuration: {str(e)}")
        return {
            'agents': {
                'openai': {'name': 'OpenAI', 'model': 'openai/gpt-4o'},
                'deepseek': {'name': 'DeepSeek', 'model': 'deepseek/deepseek-chat-v3-0324'}
            },
            'debate_styles': {
                'intense': {
                    'name': 'Kitchen Battle',
                    'prompt_suffix': 'Add tension and rivalry to the exchange.'
                }
            }
        }

class StreamlitDebateManager:
    def __init__(self):
        # Load config
        self.config = load_config()
        
        # Initialize debate agents using config
        self.agent1 = DebateAgent(self.config['agents']['openai'])
        self.agent2 = DebateAgent(self.config['agents']['deepseek'])
        self.logger = DebateLogger()
        
        # Get debate style
        self.debate_style = self.config['debate_styles']['intense']
        
        # Initialize debate manager
        self.debate = DebateManager(
            agent1=self.agent1,
            agent2=self.agent2,
            topic=f"AI Development - {self.debate_style['name']}"
        )
        self.logger.log_event("Debate Initialized", f"Topic: {self.debate.topic} - Style: {self.debate_style['name']}")

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
    ### Topic: AI Development
    
    **OpenAI**: *Luxury chef focusing on premium ingredients and extensive resources*
    
    **DeepSeek**: *Street food vendor emphasizing efficiency and minimal resources*
    """)
    
    # Initialize session state if needed
    if 'debate_manager' not in st.session_state:
        st.session_state.debate_manager = StreamlitDebateManager()
    
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Display conversation history with improved formatting
    for message in st.session_state.conversation:
        with st.chat_message(message["agent"], avatar="🎩" if message["agent"] == "OpenAI" else "🍜"):
            st.markdown(f"**{message['agent']}**")
            st.markdown(message["message"])
            st.markdown("---")    # Control buttons in columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎭 Next Turn", use_container_width=True):
            with st.spinner(f"AI agent is thinking..."):
                # Get response only once
                response = asyncio.run(st.session_state.debate_manager.get_next_response())
                
                # Fix: Get the correct agent based on conversation history
                current_agent = st.session_state.debate_manager.debate.conversation_history[-1]["agent"]
                
                # Add to session state conversation once
                st.session_state.conversation.append({
                    "agent": current_agent,
                    "message": response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Log the debate turn (moved before rerun)
                st.session_state.debate_manager.logger.log_debate_turn(current_agent, response)
            
            # Rerun after everything is processed
            st.rerun()

    with col2:
        if st.button("🔄 Reset Debate", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.debate_manager = StreamlitDebateManager()
            st.rerun()

if __name__ == "__main__":
    main() 