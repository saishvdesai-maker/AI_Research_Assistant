from openai import OpenAI
from backend.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_report():

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant. "
                        "Generate a structured academic-style report."
                    )
                },
                {
                    "role": "user",
                    "content": "Create a sample research report based on AI papers."
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Report generation failed: {str(e)}"