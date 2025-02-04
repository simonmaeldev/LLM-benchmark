# LLM-benchmark

A proxy server for benchmarking LLM models and prompts. This tool allows you to use any LLM model supported by the `llm` Python library through an OpenAI-compatible API endpoint.

## Installation

1. Make sure you have Python installed
2. Install dependencies using `uv`:
```bash
uv venv
uv pip install -r requirements.txt
```

## Usage

### 1. Start the proxy server

```bash
uv run python src/serve-proxy.py
```

This will start a server on `127.0.0.1:11435` that provides an OpenAI-compatible API endpoint.

### 2. Connect using Aider

You can use Aider with any model supported by the `llm` library. Example:

```bash
aider --openai-api-base http://0.0.0.0:11435/v1 --openai-api-key thisisnotakey --model openai/<model_name>
```

Replace `<model_name>` with any model ID supported by your `llm` installation. Some examples:
- deepseek-chat
- claude-2
- gpt-3.5-turbo

The proxy will automatically save all conversations to the `llm` database for later analysis and benchmarking.

## Features

- OpenAI-compatible API endpoint
- Automatic conversation logging
- Support for all models available in the `llm` library
- Streaming responses
