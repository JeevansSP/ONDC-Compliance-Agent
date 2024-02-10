"""LLM keys and secrets"""

OPENAI_API_KEY = ""
BRAVE_API_KEY = ""

#enter your api keys here
if not OPENAI_API_KEY or  not BRAVE_API_KEY:
    raise ValueError(f"Please enter a valid openai and brave api key")