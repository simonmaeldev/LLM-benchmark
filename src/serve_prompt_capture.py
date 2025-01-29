import datetime
import json
import dataclasses
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, Request
from llm import get_model
from llm.models import Conversation, Prompt, _BaseResponse

def conversation_to_dict(obj):
    """Convert conversation object and its nested objects to a dictionary."""
    if dataclasses.is_dataclass(obj):
        return {k: conversation_to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    elif isinstance(obj, (list, tuple)):
        return [conversation_to_dict(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: conversation_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {k: conversation_to_dict(v) for k, v in obj.__dict__.items()}
    return obj

app = FastAPI()


def generate_conversation(request: Dict[str, Any]) -> Conversation:
    model = get_model("deepseek-chat")
    conversation = model.conversation()

    # Create fake responses for the conversation history
    responses: List[_BaseResponse] = []

    for message in request.get("messages", []):
        if message["role"] == "system":
            # Create a system prompt response
            prompt = Prompt(prompt=None, model=model, system=message["content"])
        else:
            # Create a regular message response
            prompt = Prompt(prompt=message["content"], model=model)

        response = _BaseResponse(
            prompt=prompt, model=model, stream=False, conversation=conversation
        )

        # Set the response text based on role
        if message["role"] == "assistant":
            response._chunks = [message["content"]]
            response._done = True
            response._start = datetime.datetime.now().timestamp()
            response._end = response._start

        responses.append(response)

    # Set the conversation's responses
    conversation.responses = responses

    return conversation


@app.post("/v1/completions")
async def capture_completion(request: Request):
    body = await request.json()
    print("Received request:", json.dumps(body, indent=2))
    conversation = generate_conversation(body)
    # Save conversation to JSON file
    with open(f"conversation_{conversation.id}.json", "w") as f:
        json.dump(conversation_to_dict(conversation), f, indent=2, default=str)
    # Save conversation to JSON file
    with open(f"conversation_{conversation.id}.json", "w") as f:
        json.dump(conversation_to_dict(conversation), f, indent=2, default=str)
    return {"message": "Request captured", "conversation_id": conversation.id}


@app.post("/v1/chat/completions")
async def capture_chat_completion(request: Request):
    body = await request.json()
    print("Received request:", json.dumps(body, indent=2))
    conversation = generate_conversation(body)
    return {"message": "Request captured", "conversation_id": conversation.id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11435)
