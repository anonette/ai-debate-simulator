# 🍽️ Kitchen Debate: AI Culinary Showdown

Kitchen Debate is an interactive debate platform that pits two AI chef personas against each other in a battle of approaches to AI development, using cooking metaphors to make technical concepts accessible and entertaining.

## 👨‍🍳 Concept

Two AI personalities debate the merits of their approaches to AI model training:

- **OpenAI Chef**: A luxury chef who believes in premium ingredients and extensive resources
  - Represents high-resource, compute-intensive AI development
  - Uses metaphors of fine dining, slow cooking, and premium ingredients
  
- **DeepSeek Chef**: A street food vendor focused on efficiency and minimal resources
  - Represents efficient, optimized AI development approaches
  - Uses metaphors of wok cooking, efficiency, and doing more with less

## 🚀 Features

- **Dynamic AI Debates**: Real-time AI-generated responses using OpenRouter API
- **Themed Metaphors**: Technical concepts explained through cooking metaphors
- **Comprehensive Logging**: Full debate history tracked and stored
- **Multi-format Export**: Export debates as JSON, TXT, Markdown, or CSV
- **Visual Interface**: Streamlit-based UI with chef avatars and styled messages

## 📋 Requirements

- Python 3.8+
- OpenRouter API key (for accessing AI models)
- Required packages (install via `pip install -r requirements.txt`):
  - streamlit
  - python-dotenv
  - requests
  - asyncio
  - pyyaml

## 🔧 Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/KitchenDebate.git
   cd KitchenDebate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. Run the application:
   ```
   streamlit run debate_app.py
   ```

## 🎮 Usage

1. **Starting a Debate**: Click the "Next Turn" button to generate responses
2. **Stopping a Debate**: Click "Stop Debate" to end the current session
3. **Resetting**: Click "Reset Debate" to start fresh
4. **Exporting**: Use the "Export Debate" button in the sidebar to save in multiple formats

## 🧩 Project Structure

- `debate_app.py`: Main Streamlit application
- `debate_system.py`: Core debate agent implementation
- `debate_manager.py`: Manages turn-taking and conversation flow
- `debate_logger.py`: Handles logging and exporting
- `config.yaml`: Configuration for agent personalities and debate settings
- `educational_debate.py`: Simplified implementation for educational purposes
- `EDUCATIONAL_GUIDE.md`: Comprehensive guide for using the system in educational settings

## ⚙️ Configuration

The `config.yaml` file allows you to customize:

- Agent personalities and model selection
- Debate prompt templates
- Available debate topics
- Debate styles (casual, intense, philosophical)

Example configuration:

```yaml
agents:
  openai:
    name: "OpenAI"
    model: "openai/gpt-4-turbo-preview"
    personality: |
      You're OpenAI, the smug chef at the fanciest AI restaurant in town...
      
  deepseek:
    name: "DeepSeek"
    model: "deepseek/deepseek-chat"
    personality: |
      You're DeepSeek, the street-smart chef revolutionizing AI cuisine...
```

## 📊 Logging and Exports

All debates are automatically logged to the `logs/` directory:

- `logs/debate_log_[TIMESTAMP].log`: Raw log file
- `logs/debate_history_[TIMESTAMP].json`: Structured conversation history
- `logs/debate_metadata_[TIMESTAMP].json`: Debate metadata

Exported debates are saved to `logs/exports/` in multiple formats:
- JSON: Complete structured data
- TXT: Plain text transcript
- Markdown: Formatted for easy reading
- CSV: Tabular format for analysis

## 🎓 Educational Version

An educational version of the Kitchen Debate system is available for teaching purposes:

### Purpose
The educational version (`educational_debate.py`) provides a simplified implementation that demonstrates core concepts of AI conversation design, prompt engineering, and agent development. It serves as an accessible entry point for students learning about AI systems.

### Features
- **Simplified Implementation**: Clear, well-documented code designed for learning
- **Command Line Interface**: Easy to run and experiment with
- **Memory Options**: Toggle between basic (single-turn) and enhanced (full history) memory modes
- **API Flexibility**: 
  - OpenAI Chef uses OpenAI's API (GPT-3.5/4)
  - DeepSeek Chef uses OpenRouter API (DeepSeek model)
- **Placeholder Responses**: Works even without API keys for initial testing

### Usage
Run the educational debate with:
```
python educational_debate.py [--enhanced-memory] [--turns NUMBER]
```

Options:
- `--enhanced-memory`: Enable full conversation history for better context
- `--turns NUMBER`: Set the number of debate turns (default: 6)

### Requirements
- OpenAI API key (for OpenAI Chef)
- OpenRouter API key (for DeepSeek Chef)
- Create a `.env` file with these keys:
  ```
  OPENAI_API_KEY=your_openai_api_key_here
  OPENROUTER_API_KEY=your_openrouter_api_key_here
  ```

### Learning Objectives
Students can explore:
- How different prompt designs affect AI behavior
- The impact of memory on conversation coherence
- Using metaphors to explain technical concepts
- API integration with multiple AI providers
- Asynchronous programming for API calls

For a comprehensive guide on using this system for educational purposes, see `EDUCATIONAL_GUIDE.md`.

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- OpenAI and DeepSeek for the AI models
- OpenRouter for API access to multiple models
- Streamlit for the interactive web interface 
