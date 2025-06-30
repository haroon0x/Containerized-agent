from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import logging

from langchain_openai import ChatOpenAI



def call_llm_gemini(prompt):    
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"
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


def call_llm(prompt: str, system_prompt: str) -> str:
    """
    Call the Alchemyst AI Proxy using direct requests to the proxy, with a provided system prompt.
    """
    load_dotenv()
    ALCHEMYST_API_KEY = os.environ.get("ALCHEMYST_API_KEY")
    BASE_URL_WITH_PROXY = "https://platform-backend.getalchemystai.com/api/v1/proxy/default"
    llm = ChatOpenAI(
        api_key=ALCHEMYST_API_KEY,
        model="alchemyst-ai/alchemyst-c1",
        base_url=BASE_URL_WITH_PROXY,
    )
    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    return result.content

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    try:
        result = call_llm(prompt)
        print(result)
    except Exception as e:
        print(f"Error: {e}")