import logging
from datetime import datetime
import os
from pathlib import Path

class DebateLogger:
    def __init__(self, log_dir="logs"):
        # Create logs directory if it doesn't exist
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamp for log file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"debate_log_{timestamp}.log"
        
        # Configure logging
        self.logger = logging.getLogger("DebateLogger")
        self.logger.setLevel(logging.INFO)
        
        # File handler with timestamp
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_debate_turn(self, agent_name: str, message: str):
        """Log a debate turn with agent name and message"""
        self.logger.info(f"Agent: {agent_name}\nMessage: {message}\n{'-'*50}")
    
    def log_event(self, event_type: str, description: str):
        """Log general events in the debate system"""
        self.logger.info(f"Event: {event_type}\nDescription: {description}\n{'-'*50}")
    
    def log_error(self, error_type: str, error_message: str):
        """Log errors that occur during the debate"""
        self.logger.error(f"Error: {error_type}\nMessage: {error_message}\n{'-'*50}")

# Update .gitignore to exclude log files
def update_gitignore():
    gitignore_path = Path(".gitignore")
    log_ignore = "\n# Logs\nlogs/\n*.log\n"
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
        if "logs/" not in content:
            with open(gitignore_path, 'a') as f:
                f.write(log_ignore)
    else:
        with open(gitignore_path, 'w') as f:
            f.write(log_ignore)

# Usage example
if __name__ == "__main__":
    # Update gitignore
    update_gitignore()
    
    # Create logger instance
    logger = DebateLogger()
    
    # Example logs
    logger.log_event("Debate Start", "New debate session initialized")
    logger.log_debate_turn(
        "OpenAI",
        "*delicately places truffle* Our models require premium ingredients..."
    )
    logger.log_debate_turn(
        "DeepSeek",
        "*stirs wok efficiently* We achieve more with less..."
    )
    logger.log_error(
        "Connection Error",
        "Failed to connect to API endpoint"
    ) 