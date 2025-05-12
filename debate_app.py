import streamlit as st
from debate_manager import DebateManager
from debate_system import DebateAgent
import asyncio
import json
import yaml
from datetime import datetime
from debate_logger import DebateLogger
import os
from pathlib import Path

def load_config():
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            return config
    except Exception as e:
        st.error(f"Failed to load configuration: {str(e)}")
        return None

class StreamlitDebateManager:
    def __init__(self):
        # Load configuration
        self.config = load_config()
        if not self.config:
            st.error("Could not load configuration file")
            st.stop()
            
        # Debug: Print agent configurations
        print("OpenAI config:", self.config['agents']['openai']['name'])
        print("DeepSeek config:", self.config['agents']['deepseek']['name'])
        
        # Create debate ID
        self.debate_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize enhanced logger
        self.logger = DebateLogger(debate_id=self.debate_id)
        
        # Initialize debate agents
        self.agent1 = DebateAgent(
            name=self.config['agents']['openai']['name'],
            personality=self.config['agents']['openai']['personality']
        )
        self.agent2 = DebateAgent(
            name=self.config['agents']['deepseek']['name'],
            personality=self.config['agents']['deepseek']['personality']
        )
        
        # Debug: Print initialized agents
        print("Agent 1 name:", self.agent1.name)
        print("Agent 2 name:", self.agent2.name)
        
        # Initialize debate manager with topic from config (using first topic if available)
        default_topic = "AI Model Training: Efficiency vs Resources"
        self.topic = self.config.get('topics', [{'name': default_topic}])[0].get('name', default_topic)
        
        self.debate = DebateManager(
            agent1=self.agent1,
            agent2=self.agent2,
            topic=self.topic
        )
        
        # Set debate metadata
        self.logger.set_debate_metadata(
            topic=self.topic,
            agents=[
                {"name": self.agent1.name, "identity": "OpenAI", "role": "Luxury Chef"},
                {"name": self.agent2.name, "identity": "DeepSeek", "role": "Street Food Chef"}
            ]
        )
        
        self.logger.log_event("Debate Initialized", f"Topic: {self.debate.topic}")

    async def get_next_response(self):
        if not self.debate.conversation_history:
            response = await self.debate.start_debate()
            self.logger.log_event("Debate Started", "First turn initiated")
        else:
            response = await self.debate.next_turn()
        return response
    
    def end_debate(self):
        """End the debate session and finalize logs"""
        self.logger.end_debate()
        
        # Export the debate in all formats
        export_files = self.logger.export_debate("all")
        return export_files

def load_conversation_history():
    try:
        with open('debate_conversation.json', 'r') as f:
            return json.load(f)
    except:
        return []

def get_export_list():
    """Get list of available exports"""
    export_dir = Path("logs/exports")
    if not export_dir.exists():
        return []
    
    files = []
    for ext in [".txt", ".json", ".md", ".csv"]:
        files.extend(list(export_dir.glob(f"*{ext}")))
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[:10]  # Return 10 most recent

def main():
    st.title("🤖 AI Debate: OpenAI vs DeepSeek")
    
    # Load config
    config = load_config()
    if not config:
        st.error("Could not load configuration file")
        st.stop()
    
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
    
    if 'exports' not in st.session_state:
        st.session_state.exports = None

    # Sidebar for exports and logs
    with st.sidebar:
        st.subheader("Debate Controls")
        
        # Export section
        if st.button("📊 Export Debate", use_container_width=True):
            export_files = st.session_state.debate_manager.end_debate()
            st.session_state.exports = export_files
            st.success(f"Debate exported successfully!")
        
        if st.session_state.exports:
            st.subheader("Recent Exports")
            for format_type, filepath in st.session_state.exports.items():
                filename = os.path.basename(filepath)
                st.markdown(f"- [{format_type.upper()}] {filename}")
                
        # Show recent debate exports
        st.subheader("Browse Exports")
        export_files = get_export_list()
        if export_files:
            for file in export_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"{file.stem}")
                with col2:
                    ext = file.suffix.strip(".")
                    st.markdown(f"`{ext.upper()}`")
        else:
            st.info("No previous debate exports found")
        
        # Stats section
        if st.session_state.conversation:
            st.subheader("Debate Statistics")
            st.metric("Total Exchanges", len(st.session_state.conversation))
            
            # Count messages per agent
            openai_count = sum(1 for msg in st.session_state.conversation if msg["agent_identity"] == "OpenAI")
            deepseek_count = sum(1 for msg in st.session_state.conversation if msg["agent_identity"] == "DeepSeek")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("OpenAI Turns", openai_count)
            with col2:
                st.metric("DeepSeek Turns", deepseek_count)
    
    # Main content area
    # Display conversation history with improved formatting
    for message in st.session_state.conversation:
        # Debug: Print the agent name for each message
        agent_name = message["agent"]
        agent_identity = message.get("agent_identity", agent_name)  # Use explicit identity if available
        
        print(f"Displaying message from: {agent_name} (identity: {agent_identity})")
        
        # Always use avatar based on the agent's identity, not just name
        avatar = "🎩" if agent_identity == "OpenAI" else "🍜"
        
        with st.chat_message(agent_name, avatar=avatar):
            st.markdown(f"**{agent_name}**")
            st.markdown(message["message"])
            st.markdown("---")

    # Control buttons in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎭 Next Turn", use_container_width=True):
            response = asyncio.run(st.session_state.debate_manager.get_next_response())
            
            # Get the last entry from the debate manager's conversation history
            latest_entry = st.session_state.debate_manager.debate.conversation_history[-1]
            
            # Extract agent name and identity
            agent_name = latest_entry["agent"]
            agent_identity = latest_entry.get("agent_identity", agent_name)
            
            # Debug: Print the current agent
            print(f"Current agent turn: {agent_name} (identity: {agent_identity})")
            
            message_data = {
                "agent": agent_name,
                "agent_identity": agent_identity,
                "message": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.conversation.append(message_data)
            
            # Log the debate turn with correct identity
            st.session_state.debate_manager.logger.log_debate_turn(
                agent_name, 
                response,
                agent_identity
            )
            
            st.rerun()

    with col2:
        if st.button("⏹️ Stop Debate", use_container_width=True):
            export_files = st.session_state.debate_manager.end_debate()
            st.session_state.exports = export_files
            st.success("Debate stopped and exported!")

    with col3:
        if st.button("🔄 Reset Debate", use_container_width=True):
            # End current debate if any
            if st.session_state.conversation:
                st.session_state.debate_manager.end_debate()
            
            # Clear conversation and create new debate manager
            st.session_state.conversation = []
            st.session_state.debate_manager = StreamlitDebateManager()
            st.session_state.exports = None
            st.rerun()

if __name__ == "__main__":
    main() 