# ask_gpt
from pathlib import Path

api_key = 'API_KEYS_BLANK'
from openai import OpenAI
client = OpenAI(api_key = api_key)

def ask_gpt(system, user, model, temperature):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature = temperature,
    )
    return response.choices[0].message.content.strip()