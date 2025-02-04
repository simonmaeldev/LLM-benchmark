# LLM-benchmark

## Prompt Capture

This tool was initially designed to benchmark LLM models and prompts by capturing conversations through an OpenAI-compatible API endpoint. However, please note that currently the `llm` library does not automatically save conversations to a database as initially assumed, making this implementation currently non-functional for its intended benchmarking purpose.

### Installation

1. Make sure you have Python installed
2. Install dependencies using `uv`:
```bash
uv venv
uv pip install -r requirements.txt
```

### Usage

#### 1. Start the proxy server

```bash
uv run python src/serve-proxy.py
```

This will start a server on `127.0.0.1:11435` that provides an OpenAI-compatible API endpoint.

#### 2. Connect using Aider

You can use Aider with any model supported by the `llm` library. Example:

```bash
aider --openai-api-base http://0.0.0.0:11435/v1 --openai-api-key thisisnotakey --model openai/<model_name>
```

Replace `<model_name>` with any model ID supported by your `llm` installation. Some examples:
- deepseek-chat
- claude-2
- gpt-3.5-turbo

### Features

- OpenAI-compatible API endpoint
- Support for all models available in the `llm` library
- Streaming responses

### Known Limitations

- Despite initial intentions, conversations are not automatically saved to a database for benchmarking purposes
- The current implementation serves mainly as a proxy to the `llm` library without the benchmarking capabilities
