from backend.vector_store import search
from openai import OpenAI
import os


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def compare_papers():

    results = search(
        "methods results conclusion findings"
    )


    context = "\n".join(
        results["documents"][0]
    )


    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role":"system",
                "content":
                "Compare research papers and explain similarities, differences and research gaps."
            },


            {
                "role":"user",
                "content":context
            }

        ]

    )


    return response.choices[0].message.content