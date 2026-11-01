from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests


class ProviderError(RuntimeError):
    """A readable error returned by an AI provider or a connection failure."""


def _response_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            error = payload.get("error", payload)
            if isinstance(error, dict):
                return str(error.get("message") or error.get("status") or error)
            return str(error)
    except ValueError:
        pass
    return response.text[:500] or f"HTTP {response.status_code}"


def _openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    if not api_key:
        raise ProviderError("Enter an API key in the sidebar.")
    url = base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url += "/chat/completions"

    payload_messages = [{"role": "system", "content": system_prompt}]
    payload_messages.extend(messages)
    payload: dict[str, Any] = {
        "model": model,
        "messages": payload_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=(15, 180),
        )
    except requests.RequestException as exc:
        raise ProviderError(f"Could not connect to the API: {exc}") from exc

    if not response.ok:
        raise ProviderError(f"API error ({response.status_code}): {_response_error(response)}")
    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise ProviderError("The API returned an unexpected response format.") from exc
    if isinstance(content, list):
        # Some compatible providers return structured text blocks.
        content = "\n".join(str(block.get("text", "")) for block in content if isinstance(block, dict))
    if not isinstance(content, str) or not content.strip():
        raise ProviderError("The model returned an empty response.")
    return content.strip()


def _gemini(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    if not api_key:
        raise ProviderError("Enter a Gemini API key in the sidebar.")
    root = base_url.rstrip("/")
    endpoint = f"{root}/models/{quote(model, safe='')}:generateContent"
    contents = []
    for message in messages:
        role = "model" if message["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": message["content"]}]})

    payload: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if system_prompt.strip():
        payload["systemInstruction"] = {"parts": [{"text": system_prompt.strip()}]}

    try:
        response = requests.post(
            endpoint,
            params={"key": api_key},
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=(15, 180),
        )
    except requests.RequestException as exc:
        raise ProviderError(f"Could not connect to Gemini: {exc}") from exc

    if not response.ok:
        raise ProviderError(f"Gemini error ({response.status_code}): {_response_error(response)}")
    try:
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        answer = "\n".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise ProviderError("Gemini returned an unexpected or empty response.") from exc
    if not answer.strip():
        raise ProviderError("Gemini returned an empty response.")
    return answer.strip()


def _ollama(
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    payload_messages = [{"role": "system", "content": system_prompt}]
    payload_messages.extend(messages)
    payload = {
        "model": model,
        "messages": payload_messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    try:
        response = requests.post(url, json=payload, timeout=(10, 300))
    except requests.RequestException as exc:
        raise ProviderError(
            "Could not reach Ollama. Check that Ollama is running and the base URL is correct. "
            f"Details: {exc}"
        ) from exc
    if not response.ok:
        raise ProviderError(f"Ollama error ({response.status_code}): {_response_error(response)}")
    try:
        answer = response.json()["message"]["content"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ProviderError("Ollama returned an unexpected response format.") from exc
    if not isinstance(answer, str) or not answer.strip():
        raise ProviderError("Ollama returned an empty response.")
    return answer.strip()


def chat_completion(
    provider: str,
    model: str,
    base_url: str,
    api_key: str,
    messages: list[dict[str, str]],
    system_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """Route a conversation to the selected provider and return assistant text."""
    if not messages:
        raise ProviderError("Send a message first.")
    if provider == "OpenAI-compatible":
        return _openai_compatible(base_url, api_key, model, messages, system_prompt, temperature, max_tokens)
    if provider == "Gemini":
        return _gemini(base_url, api_key, model, messages, system_prompt, temperature, max_tokens)
    if provider == "Ollama (local)":
        return _ollama(base_url, model, messages, system_prompt, temperature, max_tokens)
    raise ProviderError(f"Unsupported provider: {provider}")
