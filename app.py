from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import os

app = FastAPI()

# CORS (frontend ke liye safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 API KEY (Railway me env variable se aayega)
API_KEY = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"

# ✅ TEST ROUTE (IMPORTANT)
@app.get("/")
def home():
    return {
        "status": "running",
        "api_key_loaded": API_KEY is not None
    }

# chat memory
chat_history = {}

# 🤖 AI ROUTE
@app.get("/ai")
def ai(budget: str, location: str, days: int, user_id: int):

    if API_KEY is None:
        return {"error": "API KEY NOT SET"}

    prompt = f"""
    Create a detailed travel itinerary:
    Location: {location}
    Budget: {budget}
    Days: {days}

    Include:
    - Day wise plan
    - Places to visit
    - Food suggestions
    - Budget breakdown
    """

    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({
        "role": "user",
        "content": prompt
    })

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": chat_history[user_id]
    }

    # retry logic
    for _ in range(3):
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            break
        elif response.status_code == 429:
            time.sleep(2)
        else:
            return {"error": response.status_code}

    result = response.json()

    if "choices" in result:
        answer = result["choices"][0]["message"]["content"]

        chat_history[user_id].append({
            "role": "assistant",
            "content": answer
        })

        return {"answer": answer}

    return {"error": result}
