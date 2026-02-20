import requests

COLAB_API = "https://vicarly-doubtingly-damon.ngrok-free.dev/chat"

def ask_llm(context, question):

    payload = {
        "context": context[:3000],
        "question": question
    }

    try:
        r = requests.post(COLAB_API, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["answer"]
    except Exception as e:
        return f"AI server not reachable. Make sure Colab is running.\n\nError: {e}"