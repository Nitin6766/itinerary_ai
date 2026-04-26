import os
import time
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# App init
app = FastAPI()

# CORS (safe for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_KEY = os.getenv("GROQ_API_KEY")

# API URL
url = "https://api.groq.com/openai/v1/chat/completions"

# Memory (simple)
chat_history = {}

# Root route (test)
@app.get("/")
def home():
    return {
        "status": "ok",
        "api_key_loaded": API_KEY is not None
    }

# AI route
@app.get("/ai")
async def bhakol(budget: str, location: str, days: int, user_id: int):

    # API key check
    if not API_KEY:
        return {"error": "API key missing"}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

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

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": chat_history[user_id]
    }

    try:
        max_retries = 3

        for i in range(max_retries):
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                break
            elif response.status_code == 429:
                time.sleep(3)
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

    except Exception as e:
        return {"error": str(e)}
