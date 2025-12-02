# mistral_client.py
import aiohttp
import json
import os

async def ask_mistral(question, context=""):
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return None

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": f"You are a helpful class assistant. Use this context if relevant: {context}"},
            {"role": "user", "content": question}
        ],
        "temperature": 0.5,
        "max_tokens": 300
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Mistral API Error: {e}")
        pass
    return None
