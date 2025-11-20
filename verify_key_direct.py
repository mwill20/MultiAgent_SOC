import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [{
        "parts": [{"text": "Hello"}]
    }]
}

print(f"Testing API key: {api_key[:5]}...{api_key[-5:]}")
response = requests.post(url, headers=headers, json=data)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
