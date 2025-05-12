# KitchenDebate

A creative AI debate simulator that pits different large language models against each other in a culinary-themed debate format.

## Core Concept

KitchenDebate simulates debates between AI models (like OpenAI's GPT-4 and DeepSeek's models) where they take on personas related to cooking and food preparation as metaphors for their AI development approaches. For example, OpenAI is portrayed as a "luxury chef" while DeepSeek is portrayed as a "street food vendor" - reflecting different philosophies in AI development (resource-intensive vs. efficient).

## Key Components

1. **Debate System (`debate_system.py`)**
   - Defines the `DebateAgent` class that represents each AI participant
   - Handles API connections to language models via OpenRouter
   - Each agent has a name (e.g., "OpenAI") and personality (e.g., "luxury chef")

2. **Debate Manager (`debate_manager.py`)**
   - Orchestrates the debate between two AI agents
   - Tracks conversation history and manages turns
   - Builds context for each message to maintain coherent conversation

3. **Debate Logger (`debate_logger.py`)**
   - Records all debate events and messages for future reference
   - Creates timestamped log files
   - Handles both file and console output

4. **Configuration (`config.yaml`)**
   - Contains settings for agents, models, debate topics, and styles
   - Defines debate prompts and personalities
   - Allows for different debate "styles" (Casual Dinner, Kitchen Battle, Fine Dining)

5. **Web Interface (`debate_app.py` and `app.py`)**
   - Uses Streamlit to create a web-based UI for the debates
   - Displays conversation history with appropriate formatting
   - Provides controls for advancing the debate or resetting it

6. **API Testing (`test_api.py`)**
   - Tests connections to OpenRouter API for language model access
   - Verifies API keys and configuration

## How It Works

1. The system initializes two debate agents, each representing a different AI model
2. Each agent is assigned a persona (e.g., luxury chef vs. street food vendor)
3. A debate topic is selected (e.g., "AI Model Training: Efficiency vs Resources")
4. The debate manager alternates between agents, generating responses through the language models
5. Each response is logged and displayed in the Streamlit interface
6. Users can advance the debate by clicking "Next Turn" or reset it with "Reset Debate"

## Debate Themes

The debates use culinary metaphors to represent different AI development approaches:
- Premium ingredients vs. efficient cooking (high resource usage vs. efficiency)
- Luxury dining vs. street food (different approaches to AI design)
- Complex preparation vs. simple techniques (model complexity vs. simplicity)

Available topics include:
- AI Dinner Battle: A feast where AI companies compete through food metaphors
- AI Olympics: Sports metaphors for AI competition
- AI Space Race: Space exploration metaphors for AI development

## Running the Project

### Prerequisites
- Python 3.8+
- OpenRouter API key (stored in a `.env` file)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/KitchenDebate.git
   cd KitchenDebate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

### Running the Application

Option 1: Using the runner script (recommended):
```
python run_debate.py
```

Option 2: Direct execution of Streamlit app:
```
streamlit run debate_app.py
```

## Sample Debate Output

The debates can get quite entertaining, with AI models exchanging witty culinary-themed barbs:

**OpenAI (Luxury Chef):**
> *delicately places a sliver of truffle atop a meticulously prepared dish, a monitor displaying real-time API usage in the background*
> 
> "We consider each API request not just a transaction, but a morsanet, if you will—each byte distilled from our $13B worth of premium GPUs, like extracting the rarest essence of white truffle. It's not just service; it's an art form, darling."

**DeepSeek (Street Food Vendor):**
> *slides bowl aside and checks training efficiency on phone*
> 
> "We scraped that benchmark with a fraction of the parameters - proof you don't need a 10,000 GPU kitchen to cook up SOTA results. It's all about technique and knowing your ingredients, not throwing money at the pot."

## License

This project is licensed under the terms included in the LICENSE file.

## Acknowledgments

- OpenAI and DeepSeek for their AI models
- OpenRouter for API access to multiple AI models
- Streamlit for the web interface framework
