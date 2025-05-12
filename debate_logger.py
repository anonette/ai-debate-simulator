import logging
from datetime import datetime
import os
from pathlib import Path
import json
import csv
import shutil
import re

class DebateLogger:
    def __init__(self, log_dir="logs", debate_id=None):
        # Create logs directory if it doesn't exist
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create a subdirectory for exports
        self.export_dir = self.log_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)
        
        # Create debate ID or use provided one
        self.debate_id = debate_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create log file name with debate ID
        self.log_file = self.log_dir / f"debate_log_{self.debate_id}.log"
        
        # Store debate conversation history
        self.conversation_history = []
        self.debate_metadata = {
            "id": self.debate_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "topic": None,
            "agents": []
        }
        
        # Configure logging
        self.logger = logging.getLogger(f"DebateLogger_{self.debate_id}")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers if any (to avoid duplicate logs)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler with timestamp
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
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
        
        # Save a symlink to the most recent log file
        self.create_latest_symlink()
    
    def create_latest_symlink(self):
        """Create a symlink to the latest log file for easy access"""
        latest_log = self.log_dir / "latest_debate.log"
        
        # On Windows, we need to copy since symlinks require admin privileges
        if os.name == 'nt':
            if latest_log.exists():
                latest_log.unlink()
            try:
                shutil.copy2(self.log_file, latest_log)
            except Exception as e:
                print(f"Could not create latest log copy: {e}")
        else:
            # On Unix systems, we can use a symlink
            if latest_log.exists():
                latest_log.unlink()
            try:
                latest_log.symlink_to(self.log_file.name)
            except Exception as e:
                print(f"Could not create latest log symlink: {e}")
    
    def set_debate_metadata(self, topic, agents):
        """Set metadata for the debate session"""
        self.debate_metadata["topic"] = topic
        self.debate_metadata["agents"] = agents
        self.save_metadata()
        
        # Log the debate initiation
        self.log_event("Debate Initialized", f"Topic: {topic}, Agents: {', '.join(a['name'] for a in agents)}")
    
    def log_debate_turn(self, agent_name: str, message: str, agent_identity: str = None):
        """Log a debate turn with agent name and message"""
        # Record in structured history
        turn_data = {
            "agent": agent_name,
            "agent_identity": agent_identity or agent_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(turn_data)
        
        # Log to file
        self.logger.info(f"Agent: {agent_name} ({agent_identity or agent_name})\nMessage: {message}\n{'-'*50}")
        
        # Save the updated conversation history
        self.save_conversation_history()
    
    def log_event(self, event_type: str, description: str):
        """Log general events in the debate system"""
        self.logger.info(f"Event: {event_type}\nDescription: {description}\n{'-'*50}")
    
    def log_error(self, error_type: str, error_message: str):
        """Log errors that occur during the debate"""
        self.logger.error(f"Error: {error_type}\nMessage: {error_message}\n{'-'*50}")
    
    def save_metadata(self):
        """Save debate metadata to a JSON file"""
        metadata_file = self.log_dir / f"debate_metadata_{self.debate_id}.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.debate_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_error("Metadata Save Error", str(e))
    
    def save_conversation_history(self):
        """Save the current conversation history to a JSON file"""
        history_file = self.log_dir / f"debate_history_{self.debate_id}.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_error("Conversation Save Error", str(e))
    
    def end_debate(self):
        """Mark the debate as ended and finalize logs"""
        self.debate_metadata["end_time"] = datetime.now().isoformat()
        self.save_metadata()
        self.log_event("Debate Ended", f"Total turns: {len(self.conversation_history)}")
    
    def get_safe_filename(self, filename):
        """Create a safe filename that works across all operating systems"""
        # Replace any character that's not alphanumeric, underscore, or hyphen with underscore
        safe_name = re.sub(r'[^\w\-]', '_', filename)
        return safe_name
    
    def export_debate(self, format_type="all"):
        """Export the debate in various formats
        
        Args:
            format_type: Format to export (json, txt, markdown, csv, or all)
        
        Returns:
            Dict of exported filenames
        """
        exports = {}
        # Use a timestamp format that's safe for filenames (no colons, spaces, etc.)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Always export JSON version
        if format_type in ["json", "all"]:
            json_export = self.export_dir / f"debate_export_{self.debate_id}_{timestamp}.json"
            data = {
                "metadata": self.debate_metadata,
                "conversation": self.conversation_history
            }
            with open(json_export, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            exports["json"] = str(json_export)
        
        # Export as plain text
        if format_type in ["txt", "all"]:
            txt_export = self.export_dir / f"debate_export_{self.debate_id}_{timestamp}.txt"
            with open(txt_export, 'w', encoding='utf-8') as f:
                f.write(f"AI Dinner Battle - Debate Transcript\n")
                f.write(f"Topic: {self.debate_metadata['topic']}\n")
                f.write("=" * 50 + "\n\n")
                
                for turn in self.conversation_history:
                    agent = turn["agent"]
                    identity = turn.get("agent_identity", agent)
                    # Format timestamp safely
                    turn_time = datetime.fromisoformat(turn["timestamp"])
                    time_str = turn_time.strftime("%Y-%m-%d %H:%M:%S")
                    message = turn["message"]
                    
                    f.write(f"[{time_str}] {agent} ({identity}):\n")
                    f.write(f"{message}\n\n")
            exports["txt"] = str(txt_export)
        
        # Export as markdown
        if format_type in ["markdown", "all"]:
            md_export = self.export_dir / f"debate_export_{self.debate_id}_{timestamp}.md"
            with open(md_export, 'w', encoding='utf-8') as f:
                f.write(f"# AI Dinner Battle - Debate Transcript\n\n")
                f.write(f"**Topic:** {self.debate_metadata['topic']}\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write("---\n\n")
                
                for turn in self.conversation_history:
                    agent = turn["agent"]
                    identity = turn.get("agent_identity", agent)
                    avatar = "🎩" if identity == "OpenAI" else "🍜"
                    # Format timestamp safely
                    turn_time = datetime.fromisoformat(turn["timestamp"])
                    time_str = turn_time.strftime("%H:%M:%S")
                    message = turn["message"]
                    
                    f.write(f"## {avatar} {agent}\n\n")
                    f.write(f"*{time_str}*\n\n")
                    f.write(f"{message}\n\n")
                    f.write("---\n\n")
            exports["markdown"] = str(md_export)
        
        # Export as CSV
        if format_type in ["csv", "all"]:
            csv_export = self.export_dir / f"debate_export_{self.debate_id}_{timestamp}.csv"
            with open(csv_export, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Agent", "Identity", "Message"])
                
                for turn in self.conversation_history:
                    writer.writerow([
                        turn["timestamp"],
                        turn["agent"],
                        turn.get("agent_identity", turn["agent"]),
                        turn["message"]
                    ])
            exports["csv"] = str(csv_export)
        
        self.log_event("Debate Exported", f"Formats: {', '.join(exports.keys())}")
        return exports

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
    
    # Set debate metadata
    logger.set_debate_metadata(
        topic="AI Model Training: Efficiency vs Resources",
        agents=[
            {"name": "OpenAI", "identity": "OpenAI", "role": "Luxury Chef"},
            {"name": "DeepSeek", "identity": "DeepSeek", "role": "Street Food Chef"}
        ]
    )
    
    # Example logs
    logger.log_event("Debate Start", "New debate session initialized")
    logger.log_debate_turn(
        "OpenAI",
        "*delicately places truffle* Our models require premium ingredients...",
        "OpenAI"
    )
    logger.log_debate_turn(
        "DeepSeek",
        "*stirs wok efficiently* We achieve more with less...",
        "DeepSeek"
    )
    logger.log_error(
        "Connection Error",
        "Failed to connect to API endpoint"
    )
    
    # End debate and export
    logger.end_debate()
    logger.export_debate("all") 