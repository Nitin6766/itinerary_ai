import requests
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
PORT = int(os.environ.get("PORT", 8000))


app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {"message": "working"}



API_KEY="your api key"
url="https://api.groq.com/openai/v1/chat/completions"

headers={
  "Authorization":f"Bearer {API_KEY}",
  "Content-Type":"application/json"
}
chat_history={}
@app.get("/ai")
async def bhakol(budget:str,location:str,days:int,user_id:int):
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
    chat_history[user_id]=[]
  chat_history[user_id].append({"role":"user",
                                "content":prompt})
  data={"model":"llama-3.3-70b-versatile",
        "messages":chat_history[user_id]}
  
  max_entries=3
  for i in range(max_entries):
    response=requests.post(url,headers=headers,json=data)

    if response.status_code==200:
      break
    elif response.status_code==429:
      time.sleep(3)
    else:
      return {"error":response.status_code}
  result=response.json()
  if "choices" in result:
    answer=result["choices"][0]["message"]["content"]
    chat_history[user_id].append({"role":"assistant","content":answer})
    return {"answer":answer}
  return {"error":result}
