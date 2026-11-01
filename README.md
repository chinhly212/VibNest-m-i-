# DarkGPT — independent chat explorer

A small, runnable multi-provider AI chat application with a dark Streamlit interface. This is an independent implementation inspired by the general idea of a multi-model chat explorer; it is **not** the original Codewithdark repository.

## Features

- OpenAI-compatible chat completion APIs (OpenAI and compatible gateways)
- Google Gemini `generateContent` API
- Local Ollama chat API
- SQLite conversation history
- Export chats as Markdown
- Configurable system prompt, temperature, and output-token limit
- API keys are kept in the Streamlit session and are not written to chat history

## Requirements

- Python 3.10 or newer
- An API key for the chosen hosted provider, or a running local Ollama server
- Internet access for hosted APIs

## Run locally

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Connect a provider

### OpenAI or an OpenAI-compatible service

Choose **OpenAI-compatible**, enter the API base URL (default: `https://api.openai.com/v1`), model name (default: `gpt-4o-mini`), and API key. The app calls `/chat/completions`.

### Gemini

Choose **Gemini**, enter a Gemini API key and model name (default: `gemini-2.5-flash`). The app calls Google's `generateContent` endpoint.

### Ollama

Install and start Ollama separately, pull a model, then choose **Ollama (local)**. The default URL is `http://localhost:11434`; the default model is `llama3.2`.

## Run with Docker

```bash
docker build -t darkgpt-starter .
docker run --rm -p 8501:8501 -v darkgpt-data:/app/data darkgpt-starter
```

Then visit `http://localhost:8501`.

## Project structure

```text
app.py           Streamlit user interface and chat flow
providers.py     OpenAI-compatible, Gemini, and Ollama API adapters
storage.py       SQLite chat-history persistence
requirements.txt Python dependencies
Dockerfile       Container build
.env.example     Optional environment variable template
```

## Security notes

- Do not share API keys or commit them to Git.
- API keys entered in the sidebar remain in the active Streamlit session; use a trusted machine and deployment.
- Chat transcripts are stored locally in `darkgpt.sqlite3`. They may contain sensitive text; protect the database and its backups.
- API calls are sent to the provider selected in the sidebar. Check that provider's data handling and billing policies.
- This starter is not an authentication-enabled public service. Add user authentication, rate limits, HTTPS, and per-user storage before exposing it to the internet.
