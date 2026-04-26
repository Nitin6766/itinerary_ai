@app.get("/ai")
async def bhakol(budget: str, location: str, days: int, user_id: int):

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

    chat_history[user_id].append({"role": "user", "content": prompt})

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": chat_history[user_id]
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            return {"error": response.status_code}

        result = response.json()

        if "choices" in result:
            answer = result["choices"][0]["message"]["content"]
            chat_history[user_id].append({"role": "assistant", "content": answer})
            return {"answer": answer}

        return {"error": result}

    except Exception as e:
        return {"error": str(e)}
