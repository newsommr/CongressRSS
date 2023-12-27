from openai import OpenAI
import os

def send_prompt(prompt: str):
    openai = OpenAI(
        api_key=os.environ['DEEPINFRA_API_KEY'],
        base_url="https://api.deepinfra.com/v1/openai",
    )
    chat_completion = openai.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0 # Don't want any surprises
    )
    return chat_completion.choices[0].message.content.strip() # The API returns a leading whitespace
