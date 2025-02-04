import asyncio
import json
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from llm import get_model, get_models
from llm.models import Conversation, Prompt, Response
from pydantic import BaseModel

app = FastAPI()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    model: str
    stream: bool
    temperature: float


def generate_conversation(request: ChatCompletionRequest) -> Conversation:
    """Recreate a Conversation object from request history"""
    model = get_model(request.model)
    conversation = Conversation(model=model)

    # Add all messages except last one as history
    for msg in request.messages[:-1]:
        # Handle different message types
        if msg.role == "system":
            # System messages become prompts with system instructions
            response = Response(
                prompt=Prompt(
                    prompt="",  # Empty prompt for system messages
                    model=model,
                    system=msg.content,
                    options=model.Options(),
                ),
                model=model,
                stream=False,
                conversation=conversation,
            )
        else:
            # User/assistant messages
            response = Response(
                prompt=Prompt(
                    prompt=msg.content,
                    model=model,
                    system=None,
                    options=model.Options(),
                ),
                model=model,
                stream=False,
                conversation=conversation,
            )

        # Set response properties directly
        response._chunks = [msg.content]
        response._done = True
        response._start = time.time()
        response._end = time.time()
        response.input_tokens = 0
        response.output_tokens = 0

        # For user messages, simulate attachment structure
        if msg.role == "user":
            response.prompt.attachments = [
                {"data": "about:blank", "mime_type": "text/plain", "metadata": {}}
            ]

        conversation.responses.append(response)

    return conversation


def create_chunk(
    content: str, model: str | Any, role: str = None, finish_reason: str = None
) -> str:
    """Create an SSE formatted chunk"""
    chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": str(model),
        "choices": [
            {
                "index": 0,
                "delta": {"content": content, **({"role": role} if role else {})},
                **({"finish_reason": finish_reason} if finish_reason else {}),
            }
        ],
    }
    return f"data: {json.dumps(chunk)}\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    try:
        if not request.stream:
            raise HTTPException(status_code=400, detail="Only streaming is supported")

        # Get conversation history and last message
        print("message, received, generating conversation")
        conversation = generate_conversation(request)
        last_message = request.messages[-1].content
        print("conversation generated successfully!")
        print(f"conversation: {conversation}")
        model = get_model(request.model)

        async def stream_response():
            """Stream response using llm library"""
            # First chunk with role
            # yield create_chunk("", role="assistant")

            # Get system message from last message if present
            system_message = (
                request.messages[-1].content
                if request.messages[-1].role == "system"
                else None
            )

            # Get the llm response
            print("sending the prompt...")
            response = conversation.prompt(
                last_message,
                system=system_message,
                stream=True,
                temperature=request.temperature,
            )
            print("prompt sent!")

            # Convert sync iterator to async
            def sync_iterator():
                for chunk in response:
                    print(chunk)
                    yield chunk

            # Stream chunks
            print("waiting for the answer...")
            for chunk in sync_iterator():
                yield create_chunk(chunk, model)
                await asyncio.sleep(0)  # Yield control back to event loop

            # Final chunks
            yield create_chunk("", model, finish_reason="stop")
            yield "data: [DONE]\n\n"
            print("stream response finished!")

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    for model in get_models():
        print(model.model_id)
    uvicorn.run(app, host="127.0.0.1", port=11435)
