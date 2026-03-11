"""
Centralized Gemini/Gemma API client for AlphaForge.
Uses google-genai (new SDK). Handles both Gemini and Gemma model families.
"""
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Gemma models don't support system_instruction — prepend it to content instead
_SUPPORTS_SYSTEM_PROMPT = not GEMINI_MODEL.startswith("gemma")


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


def chat(system_prompt: str, user_message: str, max_tokens: int = 2048) -> str:
    """Single-turn chat — returns text response."""
    client = _get_client()

    if _SUPPORTS_SYSTEM_PROMPT:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        )
        content = user_message
    else:
        config = types.GenerateContentConfig(max_output_tokens=max_tokens)
        content = f"{system_prompt}\n\n{user_message}"

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=content,
        config=config,
    )
    return response.text


def stream_chat(system_prompt: str, messages: list, max_tokens: int = 4096):
    """
    Multi-turn streaming chat — yields text chunks.
    messages: list of {"role": "user"/"assistant", "content": "..."}
    """
    client = _get_client()

    contents = []
    for i, msg in enumerate(messages):
        role = "user" if msg["role"] == "user" else "model"
        text = msg["content"]
        # For Gemma, inject system prompt into first user message
        if not _SUPPORTS_SYSTEM_PROMPT and i == 0 and role == "user":
            text = f"{system_prompt}\n\n{text}"
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))

    if _SUPPORTS_SYSTEM_PROMPT:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        )
    else:
        config = types.GenerateContentConfig(max_output_tokens=max_tokens)

    response = client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=contents,
        config=config,
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text
