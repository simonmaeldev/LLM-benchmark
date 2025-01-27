# Prompt capture

> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- expose an API that send the request to a provider using llm by simonw and return the responspe

## Mid-Level Objective

- Create a server that expose on 11435 (ollama port +1)
- Capture the request
- Using llm by simonw, redo the same request to a provider. (we do that to save automatically the prompt to a local db)
- Return the answer
- Must be an OpenAI compatible API endpoint

## Implementation Notes

- No need to import any external libraries see pyproject.toml for dependencies.
- Comment every function.
- For typer commands add usage examples starting with `uv run main <func name dash sep and params>`
- When code block is given in low-level tasks, use it without making changes.
- Carefully review each low-level task for exact code changes.

## Context

### Beginning context

- `pyproject.toml` (readonly)
- `src/serve_prompt_capture.py`

### Ending context

- `pyproject.toml` (readonly)
- `src/serve_prompt_capture.py`
- `src/data_types.py` (new file)

## Low-Level Tasks

> Ordered from start to finish

1. Create data_types.py

```aider
CREATE src/data_types.py
    CREATE pydantic types:
        Model(BaseModel):
            - model: str
            - key: str

        ChatCompletionRequest(BaseModel):
            -
```

2. CREATE .env.example

```aider
CREATE .env.example
need DEEP_SEEK_API_KEY
```

3. create serve_prompt_capture.py

````aider
CREATE src/serve_prompt_capture.py:

    CREATE def generate_response(model: Model,

    CREATE def main():
        serve an OpenAI compatible API endpoint on 11435 using FastAPI
        ```python
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Process the request and generate a response
    resp_content = generate_response(request.messages)

    return {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{
            "message": ChatMessage(role="assistant", content=resp_content)
        }]
    }
        ```
````
