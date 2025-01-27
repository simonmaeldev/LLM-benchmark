from fastapi import FastAPI, Request
import uvicorn
import json
from typing import Dict, Any, List
from llm import get_model
from llm.conversation import Conversation, _BaseResponse, Prompt
from dataclasses import field
import datetime

app = FastAPI()

def generate_conversation(request: Dict[str, Any]) -> Conversation:
    model = get_model(request.get("model", "gpt-3.5-turbo"))
    conversation = model.conversation()
    
    # Create fake responses for the conversation history
    responses: List[_BaseResponse] = []
    
    for message in request.get("messages", []):
        if message["role"] == "system":
            # Create a system prompt response
            prompt = Prompt(
                prompt=None,
                model=model,
                system=message["content"]
            )
        else:
            # Create a regular message response
            prompt = Prompt(
                prompt=message["content"],
                model=model
            )
        
        response = _BaseResponse(
            prompt=prompt,
            model=model,
            stream=False,
            conversation=conversation
        )
        
        # Set the response text based on role
        if message["role"] == "assistant":
            response._chunks = [message["content"]]
            response._done = True
            response._start = datetime.datetime.now().timestamp()
            response._end = response._start + 1.0  # Fake duration
            
        responses.append(response)
    
    # Set the conversation's responses
    conversation.responses = responses
    
    return conversation

@app.post("/v1/completions")
async def capture_completion(request: Request):
    body = await request.json()
    print("Received request:", json.dumps(body, indent=2))
    conversation = generate_conversation(body)
    return {"message": "Request captured", "conversation_id": conversation.id}

@app.post("/v1/chat/completions")
async def capture_chat_completion(request: Request):
    body = await request.json()
    print("Received request:", json.dumps(body, indent=2))
    conversation = generate_conversation(body)
    return {"message": "Request captured", "conversation_id": conversation.id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11435)
