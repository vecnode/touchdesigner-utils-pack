import json
import os

# OpenRouter free router: https://openrouter.ai/openrouter/free
# API still requires a Bearer key (free tier / $0 models — create one at openrouter.ai).
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"


def send_to_openrouter():
    prompt = op('user_prompt')[0, 0].val
    # Add API key here
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = "Bearer {}".format(api_key)

    client = op('openrouter_client')
    # Web Client DAT: request(url, method, header=..., data=...) — not headers/body
    client.request(
        OPENROUTER_URL,
        'POST',
        header=headers,
        data=json.dumps(payload),
    )


send_to_openrouter()
