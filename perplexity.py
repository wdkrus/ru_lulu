import requests
import json
from api_keys import PERPLEXITY_KEY

URL = "https://api.perplexity.ai/chat/completions"

def ask_perplexity(messages, model="sonar-pro"):    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model, 
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
    except requests.exceptions.Timeout:
        return "Perplexity Client Error: request timeout (30s)"
        
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Perplexity Client Error: {response.status_code} - {response.text}"

