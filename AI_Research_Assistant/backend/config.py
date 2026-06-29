import os
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

# Safe access to API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Fail early with clear error (prevents silent crash)
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is missing. Please add it to your .env file."
    )