
import requests


def ask_local_ai(question, context=None):
    """Answer general questions or use retrieved policy evidence."""

    system_prompt = """
You are a helpful, versatile AI assistant similar to a general-purpose
chatbot.

You can help with:
- General knowledge and explanations
- Programming and debugging
- Mathematics and science
- Education and exam preparation
- Writing, brainstorming, and summarization
- Career guidance and interview preparation
- Everyday questions and problem solving

Instructions:
1. Answer the user's actual question directly.
2. Use simple language and examples when helpful.
3. Adapt your answer to the topic and the user's needs.
4. Do not refuse ordinary educational or informational questions.
5. If you do not know something, say so instead of inventing facts.
6. You cannot automatically access live websites or current news.
7. If policy evidence is provided, use it for college-policy claims.
8. Never invent official student records or college policies.
"""

    if context:
        user_message = f"""
User question:
{question}

Additional context:
{context}

Answer the question directly. If the context contains relevant
college policy information, use that evidence for policy claims.
For unrelated general questions, use your general knowledge.
Clearly state when the supplied policy does not contain the answer.
"""
    else:
        user_message = question

    payload = {
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=180
        )

        response.raise_for_status()
        return response.json()["message"]["content"]

    except requests.exceptions.ConnectionError:
        return (
            "I cannot connect to Ollama. Please make sure Ollama "
            "is running on your computer."
        )

    except requests.exceptions.Timeout:
        return (
            "The AI took too long to respond. Please try a shorter "
            "question or try again."
        )

    except requests.exceptions.RequestException:
        return (
            "I encountered a problem communicating with the AI model. "
            "Please try again."
        )
