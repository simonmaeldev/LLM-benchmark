from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/v1/completions")
async def capture_completion(request: Request):
    body = await request.json()
    print("Received request:", json.dumps(body, indent=2))
    return {"message": "Request captured"}

@app.post("/v1/chat/completions")
async def capture_chat_completion(request: Request):
    body = await request.json()
    print("Received request:", json.dumps(body, indent=2))
    return {"message": "Request captured"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11435)
