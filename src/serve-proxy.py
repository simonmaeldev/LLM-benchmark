import json
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from llm import get_model
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
        # System messages become prompts with system instructions
        system = msg.content if msg.role == "system" else None
        prompt_text = msg.content if msg.role != "system" else None

        # Create a dummy response with zero token usage
        response = Response(
            prompt=Prompt(
                prompt=prompt_text, model=model, system=system, options=model.Options()
            ),
            model=model,
            stream=False,
            conversation=conversation,
        )

        # Set dummy timing and token values
        now = time.time()
        response._start = now
        response._end = now
        response.input_tokens = 0
        response.output_tokens = 0

        conversation.responses.append(response)

    return conversation


def create_chunk(content: str, role: str = None, finish_reason: str = None) -> str:
    """Create an SSE formatted chunk"""
    chunk = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo-0125",
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
        conversation = generate_conversation(request)
        last_message = request.messages[-1].content

        async def stream_response():
            """Stream response using llm library"""
            # First chunk with role
            yield create_chunk("", role="assistant")

            # Get system message from last message if present
            system_message = (
                request.messages[-1].content
                if request.messages[-1].role == "system"
                else None
            )

            # Get the llm response
            response = conversation.prompt(
                last_message,
                system=system_message,
                stream=True,
                temperature=request.temperature,
            )

            # Stream chunks
            async for chunk in response:
                yield create_chunk(chunk)

            # Final chunks
            yield create_chunk("", finish_reason="stop")
            yield "data: [DONE]\n\n"

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

    uvicorn.run(app, host="127.0.0.1", port=11435)
