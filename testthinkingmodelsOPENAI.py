import os

from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1"),
    api_key=os.environ["OPENROUTER_API_KEY"],
)

response = client.chat.completions.create(
    model="aion-labs/aion-1.0",
    messages=[{"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": "How do I train a squirrel to deliver my mail?"}],
    extra_body={"include_reasoning": True},
    stream=True,
)

# Process the streaming response
full_content = ""

for chunk in response:
    try:
        if chunk.choices[0].delta:
            if hasattr(chunk.choices[0].delta, 'content'):
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_content += content
    except AttributeError:
        continue

print("\n\nFull Response:", full_content)