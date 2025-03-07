from datetime import datetime
import json
import os
import random

class AdvancedResponseLogger:
    def __init__(self, log_file="advanced_response_logs.json"):
        self.log_file = log_file
        self.response_templates = [
            "Based on the analysis of {}, we can conclude...",
            "Considering the topic of {}, here's what we know...",
            "When examining {}, several key points emerge..."
        ]
        self.question_templates = [
            "Could you provide more details about {}?",
            "What are the implications of {} for future developments?",
            "How does {} relate to other similar concepts?",
            "Can you explain the significance of {}?"
        ]
    
    def generate_response(self, prompt):
        template = random.choice(self.response_templates)
        return template.format(prompt)
    
    def log_response(self, prompt, response):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "metadata": {
                "response_type": "generated",
                "version": "1.0"
            }
        }
        
        existing_logs = self._read_logs()
        existing_logs.append(log_entry)
        self._write_logs(existing_logs)
    
    def _read_logs(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []
    
    def _write_logs(self, logs):
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)
    
    def get_last_log(self):
        logs = self._read_logs()
        return logs[-1] if logs else None
    
    def generate_new_question(self, last_response):
        template = random.choice(self.question_templates)
        # Extract key topic from last response
        topic = last_response.split()[-1].strip('.,!?')
        return template.format(topic)

def main():
    logger = AdvancedResponseLogger()
    
    # Generate and log initial response
    initial_prompt = "artificial intelligence and its applications"
    response = logger.generate_response(initial_prompt)
    print(f"Initial response: {response}")
    
    logger.log_response(initial_prompt, response)
    
    # Generate follow-up question
    last_log = logger.get_last_log()
    if last_log:
        new_question = logger.generate_new_question(last_log['response'])
        print(f"\nFollow-up question: {new_question}")

if __name__ == "__main__":
    main()