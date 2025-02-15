# AI Debate Simulator 🤖

[![GitHub](https://img.shields.io/github/license/YOUR_USERNAME/ai-debate-simulator)](https://github.com/YOUR_USERNAME/ai-debate-simulator/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/ai-debate-simulator)](https://github.com/YOUR_USERNAME/ai-debate-simulator/stargazers)

A Streamlit application that simulates a witty debate between OpenAI and DeepSeek, styled as a culinary battle between a luxury chef and a street food vendor. Watch as they argue about AI development through creative cooking metaphors!

## Quick Start Guide

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv $HOME\.venv
$HOME\.venv\Scripts\Activate  # On Windows
source .venv/bin/activate     # On Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_api_key_here
```

## Running the Project

### Part 1: Debate Simulator
Choose one of two versions to run:

1. Basic version (local storage):
```bash
# Start the basic Streamlit debate app
streamlit run debate_app.py
```

2. Enhanced version (with cloud storage):
```bash
# Start the enhanced Streamlit debate app with Google Cloud Storage
streamlit run app.py
```

The basic version will:
- Show a debate between OpenAI and DeepSeek
- Allow progression with "Next Turn" button
- Display color-coded messages with avatars
- Enable debate reset

The enhanced version (app.py) adds:
- Google Cloud Storage integration for logs and transcripts
- Advanced UI with custom styling
- Real-time debate statistics
- Export functionality for transcripts
- Rotating log management

### Part 2: Thinking Models Testing

1. Test API Connection:
```bash
python test_api.py
```

2. Test DeepSeek Thinking:
```bash
python test_deepseek_thinking.py
```

3. Test DeepSeek Reasoning:
```bash
python deepseektesting.py
```

Each test will show:
- Blue text: Reasoning process
- Green text: Final content
- Detailed thought process

### Example Test Outputs

**DeepSeek Thinking Test:**
```
=== Testing prompt: What is deixis? ===
[Blue] Reasoning through linguistic concepts...
[Green] Deixis refers to words that...
```

**API Connection Test:**
```
Environment Debug:
API Key format: sk-or-v1-...
Success! Response: Hello, testing the connection!
```

## Overview

This project creates an engaging debate simulation where:
- OpenAI plays a luxury chef, emphasizing premium ingredients and extensive resources
- DeepSeek acts as a street food vendor, focusing on efficiency and minimal resources
- Both debate AI model training through culinary metaphors

## Project Structure 
```
debate3/
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
├── debate_app.py          # Basic Streamlit interface
├── app.py                 # Enhanced Streamlit interface with:
│    - Google Cloud Storage integration
│    - Advanced logging system
│    - Styled UI components
│    - Real-time debate transcripts
│    - Export functionality
├── debate_manager.py      # Debate flow controller
├── debate_system.py       # Agent implementation
├── debate_conversation.json # Conversation dataset
├── test_api.py            # API testing utilities
├── deepseektesting.py     # DeepSeek testing module
└── .gitignore             # Git ignore rules
```

## Dependencies

The project requires the following main dependencies:

- **Core**
  - streamlit: Web application framework
  - asyncio: Asynchronous I/O support
  - python-dotenv: Environment variable management

- **HTTP & API**
  - httpx: Modern HTTP client for Python
    - Supports both sync and async requests
    - Provides streaming capabilities
    - Compatible with Python's async/await syntax
    - Similar API to the requests library but with async support
    - Used for direct OpenRouter API communication
    - Seamless integration with Streamlit:
      ```python
      # Example in debate_app.py
      async def get_next_response(self):
          async with httpx.AsyncClient() as client:
              response = await client.post(
                  "https://openrouter.ai/api/v1/chat/completions",
                  headers=headers,
                  json=data
              )
              # Streamlit updates in real-time
              st.write(response.json()["choices"][0]["message"]["content"])
      ```
    - Handles streaming responses in Streamlit UI
    - Maintains async compatibility with Streamlit's event loop
  - aiohttp: Async HTTP client

- **Data Handling**
  - pyyaml: YAML file processing

- **Testing**
  - pytest: Testing framework
  - pytest-asyncio: Async testing support

Install all dependencies using:
```bash
pip install -r requirements.txt
``` 

## Recent Updates

- Added improved message formatting with avatars
- Implemented column-based button layout
- Added debate context and topic description
- Fixed UTF-8 encoding issues
- Enhanced visual styling with emojis and markdown

## AI Thinking Models Testing

This sub-project contains utilities for testing various AI models' thinking and reasoning capabilities.

### Test Files

#### 0. API Connection Test (`test_api.py`)
```python
# API connection testing and configuration validation
# Features:
- Validates OpenRouter API key format and presence
- Tests basic API connectivity
- Loads and validates configuration from config.yaml
- Provides detailed debugging information
```

Example usage:
```bash
python test_api.py
```

Example output:
```
Environment Debug:
Working directory: C:/dev/debate3
.env file location: C:/dev/debate3/.env
API Key format: sk-or-v1-...abcd
API Key length: 64
Starts with 'sk-or-v1-': True

Success! Response: Hello, testing the connection!
```