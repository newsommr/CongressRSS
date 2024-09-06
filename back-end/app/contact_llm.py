from openai import OpenAI
import os

def send_prompt(prompt: str):
    openai = OpenAI(
        api_key=os.environ["DEEPINFRA_API_KEY"],
        base_url="https://api.deepinfra.com/v1/openai",
    )

    chat_completion = openai.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return chat_completion.choices[
        0
    ].message.content.strip()  # The API returns a leading whitespace
