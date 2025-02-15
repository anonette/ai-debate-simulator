import streamlit as st
import yaml
import os
import asyncio
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from debate_system import DebateAgent
from debate_manager import DebateManager
import json
from logging.handlers import RotatingFileHandler
from google.cloud import storage
from io import StringIO

# Initialize Google Cloud Storage
def init_storage():
    try:
        # Check if we're running locally
        if os.path.exists('.env'):
            logger.info("Running locally, using file system storage")
            return None
            
        # Get credentials from Streamlit secrets
        creds = {
            "type": st.secrets.get("GCS_CREDENTIALS_TYPE"),
            "project_id": st.secrets.get("GCS_PROJECT_ID"),
            "private_key_id": st.secrets.get("GCS_PRIVATE_KEY_ID"),
            "private_key": st.secrets.get("GCS_PRIVATE_KEY"),
            "client_email": st.secrets.get("GCS_CLIENT_EMAIL"),
            "client_id": st.secrets.get("GCS_CLIENT_ID"),
            "auth_uri": st.secrets.get("GCS_AUTH_URI"),
            "token_uri": st.secrets.get("GCS_TOKEN_URI"),
            "auth_provider_x509_cert_url": st.secrets.get("GCS_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": st.secrets.get("GCS_CLIENT_CERT_URL")
        }
        
        # Save credentials to temporary file
        with open('temp_credentials.json', 'w') as f:
            json.dump(creds, f)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'temp_credentials.json'
        
        storage_client = storage.Client()
        bucket_name = st.secrets.get("GCS_BUCKET_NAME", "ai-dinner-battle-logs")
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            bucket = storage_client.create_bucket(bucket_name)
        return bucket
    except Exception as e:
        logger.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
        return None

# Configure logging to use Google Cloud Storage
class GCSHandler(logging.Handler):
    def __init__(self, bucket, log_file_name):
        super().__init__()
        self.bucket = bucket
        self.log_file_name = log_file_name
        self.buffer = StringIO()

    def emit(self, record):
        msg = self.format(record)
        self.buffer.write(msg + '\\n')
        # Upload to GCS
        blob = self.bucket.blob(f"logs/{self.log_file_name}")
        blob.upload_from_string(self.buffer.getvalue())

def setup_logging():
    # Get current handlers and remove them
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create new log file with session timestamp
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f'debate_session_{session_timestamp}.log'
    
    # Initialize GCS
    bucket = init_storage()
    
    # Configure logging with GCS handler
    handlers = [logging.StreamHandler()]  # Always keep console output
    if bucket:
        handlers.append(GCSHandler(bucket, log_file))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger(__name__)

# Initialize logger
logger = logging.getLogger(__name__)

# Clean up old log files at startup
def cleanup_old_logs():
    try:
        for file in os.listdir():
            if file.startswith('debate_logs_') and file.endswith('.log'):
                os.remove(file)
                logger.info(f"Cleaned up old log file: {file}")
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {str(e)}")

cleanup_old_logs()

load_dotenv()
st.set_page_config(page_title="AI Dinner Battle", layout="wide")

# Define agent avatars and colors
AGENT_STYLES = {
    "OpenAI": {
        "avatar": "👨‍🍳",  # Professional chef
        "color": "#10a37f",  # OpenAI green
        "full_name": "OpenAI",  # Shortened name
        "title": "Fine Dining Chef"  # Separate title
    },
    "DeepSeek": {
        "avatar": "🎭",  # Theater mask for drama and rebellion
        "color": "#ff6b6b",  # Warm red
        "full_name": "DeepSeek",  # Shortened name
        "title": "Street Food Chef"  # Separate title
    }
}

def load_config():
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise

def init_agents(config):
    # First try to get API key from .env file for local development
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # If not found in .env, try Streamlit secrets
    if not api_key:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.error("OpenRouter API key not found in .env file or secrets")
        st.error("OpenRouter API key not found! Please check your .env file or secrets.")
        st.stop()
    
    # Clean the API key
    api_key = api_key.strip()
    
    # Log API key details (safely)
    logger.info(f"API Key length: {len(api_key)}")
    logger.info(f"API Key format check: starts with 'sk-or-v1-': {api_key.startswith('sk-or-v1-')}")
    
    try:
        agents = [
            DebateAgent(config['agents']['openai'], api_key),
            DebateAgent(config['agents']['deepseek'], api_key)
        ]
        logger.info("Agents initialized successfully")
        return agents
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
        st.error(f"Failed to initialize agents: {str(e)}")
        st.stop()

def show_debate_stats():
    if st.session_state.conversation:
        st.sidebar.subheader("Debate Statistics")
        agent_counts = {}
        for msg in st.session_state.conversation:
            agent_counts[msg['agent']] = agent_counts.get(msg['agent'], 0) + 1
        
        # Show stats with avatars
        for agent, count in agent_counts.items():
            col1, col2 = st.sidebar.columns([1, 4])
            with col1:
                st.markdown(f"### {AGENT_STYLES[agent]['avatar']}")
            with col2:
                st.metric(
                    f"{AGENT_STYLES[agent]['full_name']}", 
                    f"{count} turns",
                    delta=None,
                    delta_color="off"
                )
        
        st.sidebar.metric("Total Exchanges", len(st.session_state.conversation))

def export_conversation():
    conversation_text = ""
    for msg in st.session_state.conversation:
        conversation_text += f"{msg['agent']}: {msg['message']}\n\n"
    return conversation_text

async def get_agent_response(agent, last_message, debate_prompt, conversation_history=None):
    try:
        logger.info(f"Getting response from {agent.name}")
        logger.debug(f"Last message: {last_message[:100]}...")
        
        response = await agent.generate_response(
            last_message,
            debate_prompt,
            conversation_history
        )
        
        logger.info(f"Got response from {agent.name} ({len(response)} chars)")
        logger.debug(f"Response: {response[:100]}...")
        
        return response
    except Exception as e:
        logger.error(f"Failed to get response from {agent.name}: {str(e)}")
        st.error(f"Failed to get response: {str(e)}")
        return None

def save_conversation_to_json(message_data):
    try:
        # Add timestamp if not present
        if 'timestamp' not in message_data:
            message_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        bucket = init_storage()
        if bucket:
            # Cloud storage mode
            conversation_file = 'debate_conversation.json'
            blob = bucket.blob(f"conversations/{conversation_file}")
            conversation = []
            if blob.exists():
                try:
                    conversation = json.loads(blob.download_as_string())
                except json.JSONDecodeError:
                    logger.warning("Could not read existing conversation file, starting fresh")
            
            conversation.append(message_data)
            blob.upload_from_string(
                json.dumps(conversation, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
        else:
            # Local file mode
            conversation_file = 'debate_conversation.json'
            conversation = []
            if os.path.exists(conversation_file):
                try:
                    with open(conversation_file, 'r', encoding='utf-8') as f:
                        conversation = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Could not read existing conversation file, starting fresh")
            
            conversation.append(message_data)
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        logger.info("Successfully saved conversation")
        
    except Exception as e:
        logger.error(f"Failed to save conversation: {str(e)}")

def export_conversation_to_text():
    try:
        text_filename = f'debate_transcript_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        content = StringIO()
        content.write("AI Dinner Battle - Debate Transcript\n")
        content.write("=" * 50 + "\n\n")
        
        if st.session_state.conversation:
            for msg in st.session_state.conversation:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                agent = msg["agent"]
                message = msg["message"]
                
                content.write(f"[{timestamp}] {agent}:\n")
                content.write(f"{message}\n\n")
            
            bucket = init_storage()
            if bucket:
                # Cloud storage mode
                blob = bucket.blob(f"transcripts/{text_filename}")
                blob.upload_from_string(content.getvalue())
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(minutes=15),
                    method="GET"
                )
                logger.info(f"Exported transcript to cloud: {text_filename}")
                return url
            else:
                # Local file mode
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(content.getvalue())
                logger.info(f"Exported transcript locally: {text_filename}")
                return text_filename
        else:
            logger.warning("No conversation to export")
            return None
                
    except Exception as e:
        logger.error(f"Failed to export conversation: {str(e)}")
        return None

def manage_old_logs(max_logs=10):
    """Keep only the most recent N session logs"""
    try:
        # Get all debate session logs (both regular and full logs)
        logs = [f for f in os.listdir() if 
                (f.startswith('debate_session_') and 
                 (f.endswith('.log') or f.endswith('_full.log')))]
        # Sort by modification time (newest first)
        logs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Remove old logs beyond max_logs
        for old_log in logs[max_logs:]:
            os.remove(old_log)
            print(f"Removed old session log: {old_log}")
    except Exception as e:
        print(f"Error managing old logs: {str(e)}")

def setup_debate_log():
    """Create a new debate log file for the session"""
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debate_log_file = f'debate_session_{session_timestamp}_full.log'
    
    with open(debate_log_file, 'w') as f:
        f.write("=== AI Dinner Battle Debate Log ===\n")
        f.write(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
    return debate_log_file

def log_debate_message(log_file: str, agent: str, message: str, is_thinking: bool = False):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"[{timestamp}] {agent}"
        content += " is thinking...\n" if is_thinking else f":\n{message}\n\n"
        
        bucket = init_storage()
        if bucket:
            # Cloud storage mode
            blob = bucket.blob(f"debate_logs/{log_file}")
            current_content = ""
            if blob.exists():
                current_content = blob.download_as_string().decode('utf-8')
            blob.upload_from_string(current_content + content)
        else:
            # Local file mode
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(content)
        
    except Exception as e:
        logger.error(f"Failed to log debate message: {str(e)}")

def main():
    # Set up new logging session when starting new debate
    if 'config' not in st.session_state:
        cleanup_old_logs()  # Clean up old format logs
        manage_old_logs()   # Manage session logs
        
        global logger
        logger = setup_logging()
        logger.info("Starting new debate session")
        
        # Set up debate log file
        st.session_state.debate_log_file = setup_debate_log()
        logger.info(f"Created debate log file: {st.session_state.debate_log_file}")
        
        st.session_state.config = load_config()
        st.session_state.agents = init_agents(st.session_state.config)
        st.session_state.conversation = []
        st.session_state.current_speaker = 0
        st.session_state.debate_active = False
        st.session_state.debate_speed = 5
    
    # Title with styled header
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@400;600&display=swap');
        
        /* Main title styling */
        h1 {
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            color: #1E1E1E;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Custom styling for chat messages */
        .stChatMessage {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            background: white;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        /* Add some hover effects */
        .stChatMessage:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        /* Style the avatars */
        .stChatMessageAvatar {
            font-size: 2rem;
            padding: 0.75rem;
            border-radius: 50%;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Message container styling */
        .message-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Timeline styling */
        .timeline {
            position: relative;
            padding-left: 2rem;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #eee;
        }
        
        /* Message bubble styling */
        .stChatMessage {
            position: relative;
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        /* Timestamp styling */
        .message-timestamp {
            position: absolute;
            left: -6rem;
            top: 0.5rem;
            font-size: 0.8em;
            color: #999;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        /* Improved message content */
        .message-content {
            font-size: 1.05em;
            line-height: 1.5;
            color: #2C3E50;
        }
        
        /* Action text styling */
        .action-text {
            font-style: italic;
            color: #666;
            background: rgba(0,0,0,0.02);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            font-size: 0.95em;
        }
        
        /* Dialogue text styling */
        .dialogue-text {
            padding: 0.5rem 0;
            color: #2C3E50;
        }
        
        /* Agent header styling */
        .agent-header {
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        .agent-avatar {
            font-size: 1.5em;
            margin-right: 0.5rem;
        }
        
        .agent-info {
            flex-grow: 1;
        }
        
        /* Profile card styling */
        .profile-card {
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .profile-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        /* Control panel styling */
        .stButton button {
            font-family: 'Source Sans Pro', sans-serif;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
    </style>
    
    <h1 style='text-align: center; margin-bottom: 2rem; padding: 2rem 0;'>
        🍽️ AI Dinner Battle
    </h1>
    """, unsafe_allow_html=True)
    
    # Show agent profiles at the top
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='profile-card' style='background-color: {AGENT_STYLES['OpenAI']['color']}11;'>
            <div style='font-size: 2.5em; margin-bottom: 0.5rem;'>{AGENT_STYLES['OpenAI']['avatar']}</div>
            <div style='font-family: "Playfair Display", serif;'>
                <strong style='font-size: 1.2em; color: {AGENT_STYLES['OpenAI']['color']};'>{AGENT_STYLES['OpenAI']['full_name']}</strong>
                <br/>
                <span style='color: {AGENT_STYLES['OpenAI']['color']}99;'>{AGENT_STYLES['OpenAI']['title']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='profile-card' style='background-color: {AGENT_STYLES['DeepSeek']['color']}11;'>
            <div style='font-size: 2.5em; margin-bottom: 0.5rem;'>{AGENT_STYLES['DeepSeek']['avatar']}</div>
            <div style='font-family: "Playfair Display", serif;'>
                <strong style='font-size: 1.2em; color: {AGENT_STYLES['DeepSeek']['color']};'>{AGENT_STYLES['DeepSeek']['full_name']}</strong>
                <br/>
                <span style='color: {AGENT_STYLES['DeepSeek']['color']}99;'>{AGENT_STYLES['DeepSeek']['title']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Control panel
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎬 Start New Debate", key="start_button"):
            logger.info("Starting new debate")
            st.session_state.conversation = []
            st.session_state.current_speaker = 0
            st.session_state.debate_active = True
            st.rerun()
    
    with col2:
        if st.button("🛑 Stop Debate", key="stop_button"):
            logger.info("Stopping debate")
            st.session_state.debate_active = False
            st.info("Debate stopped")
    
    with col3:
        st.session_state.debate_speed = st.slider(
            "⏱️ Response Delay", 
            min_value=1, 
            max_value=10, 
            value=st.session_state.debate_speed
        )
    
    with col4:
        if st.button("📝 Export Transcript", key="export_button"):
            filename = export_conversation_to_text()
            if filename:
                st.success(f"Debate transcript exported to {filename}")
            else:
                st.error("Failed to export transcript")
    
    # Display conversation with avatars and styled messages
    st.markdown("<div class='message-container'><div class='timeline'>", unsafe_allow_html=True)
    
    # Reverse the conversation list to show newest messages first
    for msg in reversed(st.session_state.conversation):
        with st.chat_message(
            name=msg["agent"], 
            avatar=AGENT_STYLES[msg["agent"]]['avatar']
        ):
            # Split message into action and dialogue
            message = msg["message"]
            parts = message.split('"', 2)
            
            if len(parts) >= 2:
                action = parts[0].strip()
                dialogue = parts[1].strip()
                
                st.markdown(f"""
                <div class='agent-header'>
                    <div class='agent-avatar'>{AGENT_STYLES[msg["agent"]]['avatar']}</div>
                    <div class='agent-info'>
                        <span class='agent-name' style='color: {AGENT_STYLES[msg["agent"]]["color"]};'>
                            {AGENT_STYLES[msg["agent"]]["full_name"]}
                        </span>
                        <span class='agent-title'>• {AGENT_STYLES[msg["agent"]]["title"]}</span>
                    </div>
                </div>
                <div class='message-content'>
                    <div class='action-text'>{action}</div>
                    <div class='dialogue-text'>{dialogue}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='agent-header'>
                    <div class='agent-avatar'>{AGENT_STYLES[msg["agent"]]['avatar']}</div>
                    <div class='agent-info'>
                        <span class='agent-name' style='color: {AGENT_STYLES[msg["agent"]]["color"]};'>
                            {AGENT_STYLES[msg["agent"]]["full_name"]}
                        </span>
                        <span class='agent-title'>• {AGENT_STYLES[msg["agent"]]["title"]}</span>
                    </div>
                </div>
                <div class='message-content'>
                    {message}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Continue debate if active
    if st.session_state.debate_active:
        current_agent = st.session_state.agents[st.session_state.current_speaker]
        logger.info(f"Current speaker: {current_agent.name}")
        
        # Log thinking state
        log_debate_message(st.session_state.debate_log_file, current_agent.name, "", True)
        
        # Show thinking indicator with colored avatar
        with st.spinner(f"{AGENT_STYLES[current_agent.name]['avatar']} {AGENT_STYLES[current_agent.name]['full_name']} is thinking..."):
            last_message = (st.session_state.conversation[-1]["message"] 
                          if st.session_state.conversation 
                          else "Start the debate by introducing yourself and your approach to AI development.")
            
            logger.info(f"Getting response from {current_agent.name}")
            response = asyncio.run(get_agent_response(
                current_agent,
                last_message,
                st.session_state.config['debate_prompt'],
                st.session_state.conversation
            ))
            
            if response:
                logger.info(f"Adding response from {current_agent.name}")
                # Log the debate message
                log_debate_message(st.session_state.debate_log_file, current_agent.name, response)
                
                message_data = {
                    "agent": current_agent.name,
                    "message": response,
                    "recipient": st.session_state.agents[1 - st.session_state.current_speaker].name
                }
                
                # Save to conversation JSON file
                save_conversation_to_json(message_data)
                
                st.session_state.conversation.append({
                    "agent": current_agent.name,
                    "message": response
                })
                st.session_state.current_speaker = 1 - st.session_state.current_speaker
                time.sleep(st.session_state.debate_speed)
                st.rerun()
            else:
                error_msg = f"Failed to get response from {current_agent.name}"
                logger.error(error_msg)
                # Log the error in debate log
                log_debate_message(st.session_state.debate_log_file, "System", f"Error: {error_msg}")
                st.error(error_msg)
                st.session_state.debate_active = False

if __name__ == "__main__":
    main() 