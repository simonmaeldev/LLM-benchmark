import time
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, Request
from llm import get_model
from llm.models import Conversation, Prompt, _BaseResponse

app = FastAPI()


def generate_conversation(request: Dict[str, Any]) -> Conversation:
    model = get_model("deepseek-chat")
    conversation = model.conversation()
    responses: List[_BaseResponse] = []
    conv_start = time.time()
    last_user_response = None

    for idx, message in enumerate(request.get("messages", [])):
        ts = conv_start + idx * 0.000001  # Microsecond offsets

        if message["role"] == "system":
            prompt = Prompt(
                prompt="",
                model=model,
                system=message["content"],
                options=model.Options(),
            )
            response = _BaseResponse(prompt, model, False, conversation)
            response._done = True
            response.input_tokens = 0
            response.output_tokens = 0
            response._start = ts
            response._end = ts
            responses.append(response)
        elif message["role"] == "user":
            prompt = Prompt(message["content"], model=model, options=model.Options())
            response = _BaseResponse(prompt, model, False, conversation)
            responses.append(response)
            last_user_response = response
        elif message["role"] == "assistant" and last_user_response:
            last_user_response._chunks = [message["content"]]
            last_user_response._done = True
            last_user_response.input_tokens = 0
            last_user_response.output_tokens = 0
            last_user_response._start = ts
            last_user_response._end = ts
            last_user_response = None

    conversation.responses = responses
    return conversation


def to_openai_format(response: _BaseResponse, conversation_id: str):
    return {
        "id": conversation_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "deepseek-chat",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response.text()},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": response.input_tokens or 0,
            "completion_tokens": response.output_tokens or 0,
            "total_tokens": (response.input_tokens or 0)
            + (response.output_tokens or 0),
        },
    }


@app.post("/v1/chat/completions")
async def handle_chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    if not messages or messages[-1]["role"] != "user":
        return {"error": "Last message must be from user"}, 400

    # Process history
    conversation = generate_conversation({"messages": messages[:-1]})

    # Process final user message
    final_response = conversation.prompt(messages[-1]["content"])

    # Return OpenAI-compatible response
    return to_openai_format(final_response, conversation.id)


@app.post("/v1/completions")
async def handle_completion(request: Request):
    # Implement similar logic for completions endpoint if needed
    return {"error": "Not implemented"}, 501


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11435)
