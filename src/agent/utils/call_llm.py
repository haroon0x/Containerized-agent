from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import logging

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

def call_llm(prompt):    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        raise e

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    try:
        result = call_llm(prompt)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
