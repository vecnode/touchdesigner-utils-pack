import json

def send_to_ollama():
    base_url = 'http://localhost:11434/api/chat'
    model_name = 'gemma3:1b'  # your specific model string

    prompt = op('user_prompt')[0, 0].val

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    client = op('ollama_client')
    # Web Client DAT: request(url, method, header=..., data=...) — not headers/body
    client.request(
        base_url,
        'POST',
        header=headers,
        data=json.dumps(payload),
    )


send_to_ollama()
