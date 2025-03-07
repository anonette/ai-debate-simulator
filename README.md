# AI Debate Simulator experiments 🤖

This repository contains three interconnected AI research projects:

## 1. AI Debate Experiment: English vs Basque

A comparative study of AI debates in different linguistic structures.

This project implements parallel debates about AI democratization in English and Basque languages, exploring how language structure influences AI governance discussions.

## Quick Start

### 1. Environment Setup
```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY='your_key_here'
```

### 2. Running the Debates

Run both debates simultaneously in separate terminals:

Terminal 1 (English):
```bash
python gpu_debate.py
```

Terminal 2 (Basque):
```bash
python basquedebate.py
```

## Project Structure

### Debate Files
- `gpu_debate.py`: English debate implementation
- `basquedebate.py`: Basque (Euskara) debate implementation

### Logs Structure
```
logs/
├── english/              # English debate transcripts
│   └── YYYYMMDD_HHMMSS/ # Date-organized folders
├── basque/              # Basque debate transcripts
│   └── YYYYMMDD_HHMMSS/ # Date-organized folders
└── README.md            # Log documentation
```

## Raw Debate Logs

Access the raw debate transcripts from our experiments:
- [View Raw Debate Logs](https://drive.google.com/drive/folders/1H_4D9rxHQw8cksLxJ8W-mfGF_3fz0bfL?usp=drive_link)

Available files:
- `debate_basque_20250307_145443.txt`: Basque language debate transcript
- `debate_english_20250307_150535.txt`: English language debate transcript

## Research Analysis

This project includes a detailed analysis of how language structure influences AI governance debates, comparing discussions in English (nominative-accusative) and Basque (ergative-absolutive) using Gemini-Pro.

### Key Research Points
- **Linguistic Comparison**: Analysis of debates in English vs Basque
- **Agency & Structure**: How different language structures affect AI's conceptualization of control and responsibility
- **Governance Models**: Comparison between competitive (English) and collective (Basque) frameworks
- **Ethical Implications**: Impact of linguistic structures on AI governance perspectives

For detailed analysis and findings, see [debateLogAnalysis.md](debateLogAnalysis.md)

## Features
- Real-time parallel debates
- Identical Gemini-Pro models debating with each other
- Minimal prompting to allow organic discussion
- Live streaming of responses
- Automatic transcript logging
- Progress indicators during model thinking

## Requirements
- OpenRouter API key
- Python packages:
  - requests
  - datetime

## Contributing
Feel free to open issues or submit pull requests to improve the experiment.

## 2. DeepSeek Reasoning Analysis

Testing DeepSeek's reasoning capabilities through OpenRouter API.

### Features
- Stream-based reasoning analysis
- Real-time thought process visualization
- Color-coded output (Blue: reasoning, Default: content)
- Detailed reasoning breakdown

### Usage
```bash
python deepseektesting.py
```

Example output:
```
[Blue] Analyzing economic implications...
Universal Basic Income impacts include...
```

## 3. Debate System Framework

A modular system for implementing AI debates with different personalities.

### Features
- Customizable debate agents
- Personality-based responses
- JSON-based conversation management
- UTF-8 encoding support

### Usage
```python
from debate_system import DebateAgent

agent = DebateAgent(name="Agent1", personality="analytical")
response = await agent.generate_response(context, last_message)
```

## Common Requirements

- OpenRouter API key
- Python packages:
  - requests
  - httpx
  - python-dotenv
  - datetime
  - json

## Project Interconnections

These projects work together to:
1. Study AI reasoning (DeepSeek Testing)
2. Implement structured debates (Debate System)
3. Compare linguistic influences (English vs Basque Experiment)

## 4. DeepSeek vs OpenAI Culinary Debate

A creative debate simulation where AI models argue about AI development through culinary metaphors.

### Concept
- **OpenAI**: Takes the role of a luxury chef (representing resource-intensive AI development)
- **DeepSeek**: Acts as a street food vendor (representing efficient, accessible AI development)

### Features
- Metaphorical debate through cooking analogies
- Real-time response streaming
- Color-coded messages with avatars
- Debate progression with "Next Turn" button
- Debate reset capability

### Running the Debate
```bash
# Start the basic Streamlit debate app
streamlit run debate_app.py

# Or run the enhanced version with cloud storage
streamlit run app.py
```

### Enhanced Version Features
- Google Cloud Storage integration
- Advanced UI with custom styling
- Real-time debate statistics
- Export functionality
- Rotating log management

For more details on the culinary debate setup and metaphors, see the original project documentation.