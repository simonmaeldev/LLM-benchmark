# proxy for chat completion

> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- create a proxy for a chat completion conversation
- the goal is to use the python library llm to make the requests : it saves automatically all the requests in a db, allowing me to do a benchmark later on

## Mid-Level Objective

- create a server that runs on 127.0.0.1:11435 using fastapi and uvicorn
- recreate the conversation received from the request using `llm`
- send the last message of the conversation to the model
- stream back the response

## Implementation Notes

- Use only the dependencies listed in pyproject.toml
- Comment every function thoroughly
- Carefully review each low-level task for precise code changes
- Use pydantic to manage datatypes

## Context

### Beginning Context

- `pyproject.toml` (readonly)
- `original.json` (readonly)
- `src/print_to_json.py` (readonly)

### Ending Context

- `pyproject.toml` (readonly)
- `original.json` (readonly)
- `src/print_to_json.py` (readonly)
- `src/serve-proxy.py` (new)

## Low-Level Tasks

> Ordered from start to finish

1. Create src/serve-proxy.py

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import time
import uuid
from datetime import datetime

app = FastAPI()

def create_chunk(content: str, role: Optional[str] = None, finish_reason: Optional[str] = None) -> str:
    """Create a chunk in OpenAI's format"""
    response = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "your-model-name",
        "system_fingerprint": f"fp_{uuid.uuid4().hex[:10]}",
        "choices": [{
            "index": 0,
            "delta": {},
            "logprobs": None,
            "finish_reason": finish_reason
        }]
    }

    if role:
        response["choices"][0]["delta"]["role"] = role
    if content:
        response["choices"][0]["delta"]["content"] = content

    return f"data: {json.dumps(response)}\n\n"

async def stream_response(prompt: str) -> str:
    """
    Generator function that yields response chunks.
    Replace this with your actual model integration.
    """
    # First chunk: role
    yield create_chunk("", role="assistant")

    # Get the llm response and stream it back
    response = model.prompt(prompt)
    for chunk in response:
        yield create_chunk(chunk)

    # Final chunk: finish reason
    yield create_chunk("", finish_reason="stop")
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    try:
        if not request.stream:
            raise HTTPException(status_code=400, detail="Only streaming is supported")

        # Construct prompt from messages
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])

        return StreamingResponse(
            stream_response(prompt),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. modify src/serve-proxy.py

````aider
add def generate_conversation(request: JSON) -> Conversation:

    ```python
    import llm

    model = llm.get_model()
    conversation: Conversation = model.conversation()
    ```
````

3. modify src/serve-proxy.py generate_conversation

````aider
modify the generate_conversation method:

it will receive a json object that looks like this:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Act as an expert software developer.\nTake requests for changes to the supplied code.\nIf the request is ambiguous, ask questions.\n\nAlways reply to the user in the same language they are using.\n\n\nOnce you understand the request you MUST:\n1. Determine if any code changes are needed.\n2. Explain any needed changes.\n3. If changes are needed, output a copy of each file that needs changes.\n\nTo suggest changes to a file you MUST return the entire content of the updated file.\nYou MUST use this *file listing* format:\n\npath/to/filename.js\n```\n// entire file content ...\n// ... goes in between\n```\n\nEvery *file listing* MUST use this format:\n- First line: the filename with any originally provided path; no extra markup, punctuation, comments, etc. **JUST** the filename with path.\n- Second line: opening ```\n- ... entire content of the file ...\n- Final line: closing ```\n\nTo suggest changes to a file you MUST return a *file listing* that contains the entire content of the file.\n*NEVER* skip, omit or elide content from a *file listing* using \"...\" or by adding comments like \"... rest of code...\"!\nCreate a new file you MUST return a *file listing* which includes an appropriate filename, including any appropriate path.\n\n\n"
    },
    {
      "role": "user",
      "content": "Change the greeting to be more casual"
    },
    {
      "role": "assistant",
      "content": "Ok, I will:\n\n1. Switch the greeting text from \"Hello\" to \"Hey\".\n\nshow_greeting.py\n```\nimport sys\n\ndef greeting(name):\n    print(f\"Hey {name}\")\n\nif __name__ == '__main__':\n    greeting(sys.argv[1])\n```\n"
    },
    {
      "role": "user",
      "content": "I switched to a new code base. Please don't consider the above files or try to edit them any longer."
    },
    {
      "role": "assistant",
      "content": "Ok."
    },
    {
      "role": "user",
      "content": "Here are summaries of some files present in my git repository.\nDo not propose changes to these files, treat them as *read-only*.\nIf you need to edit any of these files, ask me to *add them to the chat* first.\n\n.gitignore\n\n.python-version\n\nREADME.md\n\npyproject.toml\n\nspecs/spec-benchmark-creation.md\n\nspecs/spec-benchmark-creation_v0.md\n\nsrc/serve_prompt_capture.py\n\nuv.lock\n"
    },
    {
      "role": "assistant",
      "content": "Ok, I won't try and edit those files without asking first."
    },
    {
      "role": "user",
      "content": "Don't try and edit any existing code without asking me to add the files to the chat!\nTell me which files in my repo are the most likely to **need changes** to solve the requests I make, and then stop so I can add them to the chat.\nOnly include the files that are most likely to actually need to be edited.\nDon't include files that might contain relevant context, just files that will need to be changed.\n"
    },
    {
      "role": "assistant",
      "content": "Ok, based on your requests I will suggest which files need to be edited and then stop and wait for your approval."
    },
    {
      "role": "user",
      "content": "this is a test. It might return an error"
    },
    {
      "role": "assistant",
      "content": "ok, this is the code change"
    },
    {
      "role": "user",
      "content": "create src/main.py in which you implement the fibonacci sequence\n\nTo suggest changes to a file you MUST return the entire content of the updated file.\nYou MUST use this *file listing* format:\n\npath/to/filename.js\n```\n// entire file content ...\n// ... goes in between\n```\n\nEvery *file listing* MUST use this format:\n- First line: the filename with any originally provided path; no extra markup, punctuation, comments, etc. **JUST** the filename with path.\n- Second line: opening ```\n- ... entire content of the file ...\n- Final line: closing ```\n\nTo suggest changes to a file you MUST return a *file listing* that contains the entire content of the file.\n*NEVER* skip, omit or elide content from a *file listing* using \"...\" or by adding comments like \"... rest of code...\"!\nCreate a new file you MUST return a *file listing* which includes an appropriate filename, including any appropriate path.\n\n\n"
    }
  ],
  "model": "TestModelName",
  "stream": true,
  "temperature": 0
}
````

Normally to create a conversation using llm, we do like this:

````python

import os
import sys

import llm

# Now you can import from print_to_json
from print_to_json import print_json

model = llm.get_model("deepseek-chat")
conversation = model.conversation()


def run():
    response = conversation.prompt(
        "change the gretting to be more casual",
        system='Act as an expert software developer.\nTake requests for changes to the supplied code.\nIf the request is ambiguous, ask questions.\n\nAlways reply to the user in the same language they are using.\n\n\nOnce you understand the request you MUST:\n1. Determine if any code changes are needed.\n2. Explain any needed changes.\n3. If changes are needed, output a copy of each file that needs changes.\n\nTo suggest changes to a file you MUST return the entire content of the updated file.\nYou MUST use this *file listing* format:\n\npath/to/filename.js\n```\n// entire file content ...\n// ... goes in between\n```\n\nEvery *file listing* MUST use this format:\n- First line: the filename with any originally provided path; no extra markup, punctuation, comments, etc. **JUST** the filename with path.\n- Second line: opening ```\n- ... entire content of the file ...\n- Final line: closing ```\n\nTo suggest changes to a file you MUST return a *file listing* that contains the entire content of the file.\n*NEVER* skip, omit or elide content from a *file listing* using "..." or by adding comments like "... rest of code..."!\nCreate a new file you MUST return a *file listing* which includes an appropriate filename, including any appropriate path.\n\n\n',
    )
    for chunk in response:
        print(chunk, end="")

    response2 = conversation.prompt(
        "I switched to a new code base. Please don't consider the above files or try to edit them any longer."
    )
    print(response2.text())

    response3 = conversation.prompt(
        "Here are summaries of some files present in my git repository.\nDo not propose changes to these files, treat them as *read-only*.\nIf you need to edit any of these files, ask me to *add them to the chat* first.\n\n.gitignore\n\n.python-version\n\nREADME.md\n\npyproject.toml\n\nspecs/spec-benchmark-creation.md\n\nspecs/spec-benchmark-creation_v0.md\n\nsrc/serve_prompt_capture.py\n\nuv.lock\n"
    )
    for chunk in response3:
        print(chunk, end="")

    print_json(conversation, "original.json")


run()
````

You can see what this conversation object with real responses from deepseek-chat inside the file original.json.
Here's part of the source code detail of a Conversation object:

```python
@dataclass
class _BaseConversation:
    model: "_BaseModel"
    id: str = field(default_factory=lambda: str(ULID()).lower())
    name: Optional[str] = None
    responses: List["_BaseResponse"] = field(default_factory=list)

    @classmethod
    def from_row(cls, row):
        from llm import get_model

        return cls(
            model=get_model(row["model"]),
            id=row["id"],
            name=row["name"],
        )


@dataclass
class Conversation(_BaseConversation):
    def prompt(
        self,
        prompt: Optional[str],
        *,
        attachments: Optional[List[Attachment]] = None,
        system: Optional[str] = None,
        stream: bool = True,
        **options,
    ) -> "Response":
        return Response(
            Prompt(
                prompt,
                model=self.model,
                attachments=attachments,
                system=system,
                options=self.model.Options(**options),
            ),
            self.model,
            stream,
            conversation=self,
        )


@dataclass
class AsyncConversation(_BaseConversation):
    def prompt(
        self,
        prompt: Optional[str],
        *,
        attachments: Optional[List[Attachment]] = None,
        system: Optional[str] = None,
        stream: bool = True,
        **options,
    ) -> "AsyncResponse":
        return AsyncResponse(
            Prompt(
                prompt,
                model=self.model,
                attachments=attachments,
                system=system,
                options=self.model.Options(**options),
            ),
            self.model,
            stream,
            conversation=self,
        )


class _BaseResponse:
    """Base response class shared between sync and async responses"""

    prompt: "Prompt"
    stream: bool
    conversation: Optional["_BaseConversation"] = None

    def __init__(
        self,
        prompt: Prompt,
        model: "_BaseModel",
        stream: bool,
        conversation: Optional[_BaseConversation] = None,
    ):
        self.prompt = prompt
        self._prompt_json = None
        self.model = model
        self.stream = stream
        self._chunks: List[str] = []
        self._done = False
        self.response_json = None
        self.conversation = conversation
        self.attachments: List[Attachment] = []
        self._start: Optional[float] = None
        self._end: Optional[float] = None
        self._start_utcnow: Optional[datetime.datetime] = None
        self.input_tokens: Optional[int] = None
        self.output_tokens: Optional[int] = None
        self.token_details: Optional[dict] = None
        self.done_callbacks: List[Callable] = []
```

Recreate a Conversation object using the same message content as what we receive.

- input_tokens and output_tokens are 0, as these are fake messages, they didn't cost me any tokens
- start and end are the same time, for the same reason

````

4. Modify src/serve-proxy.py
```aider
modify src/serve-proxy:
    - modify chat_completion: create a conversation using all messages except the last one
    - send a request using 'conversation.prompt(last_message)'
    - stream the response back
````
