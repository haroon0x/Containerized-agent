from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import logging
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

IS_WINDOWS = os.name == "nt"

CD_CMD = "echo %cd%" if IS_WINDOWS else "pwd"
LS_CMD = "dir" if IS_WINDOWS else "ls -la"

SYSTEM_PROMPT = '''
You are a task analysis AI that converts user requests into structured JSON action plans.

IMPORTANT:
- Output ONLY valid JSON.
- Do NOT use triple backticks, code fences, or markdown formatting.
- Do NOT include any explanations, comments, or extra text.
- The response must be a single valid JSON object, and nothing else.

For each task, analyze what actions are needed and return a JSON object with this structure:
{
  "actions": [
    {
      "type": "shell_command" | "python_code" | "file_operation",
      "description": "what this action does",
      "command": "the actual command, code, or file content to execute",
      "filename": "(required for file_operation) the filename to write to",
      "operation": "(optional for file_operation) write|append|create_directory, defaults to write"
    }
  ],
  "estimated_time": "time estimate",
  "requirements": ["list", "of", "requirements"]
}

Examples:
- For "echo hello": use shell_command with command="echo 'Hello World'"
- For "create a Python file": use file_operation with filename and command containing the Python code
- For "calculate sum": use python_code with command containing the calculation code
- For "create directory": use file_operation with operation="create_directory"

ALWAYS return a single valid JSON object, with no markdown, no code fences, and no extra text.
'''

def call_llm(prompt):    
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set. Cannot call LLM.")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        result = response.text
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            logging.error("LLM did not return valid JSON. Response was: %s", result)
            raise ValueError("LLM did not return valid JSON. See logs for details.")
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        raise

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    try:
        result = call_llm(prompt)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
