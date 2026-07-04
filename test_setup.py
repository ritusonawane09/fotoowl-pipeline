"""
Quick sanity check: confirms your .env file, API key, and Gemini connection
all work before we build anything real.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def main() -> None:
    # Load variables from .env into the environment
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")

    print("API key loaded successfully (starts with):", api_key[:5] + "...")

    # Create a Gemini model client
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

    # Send a simple test message
    response = llm.invoke("Reply with exactly one sentence confirming you received this message.")

    print("\nGemini responded:")
    print(response.content)


if __name__ == "__main__":
    main()
