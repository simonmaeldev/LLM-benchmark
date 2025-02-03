import json
from datetime import datetime

from llm.models import Conversation


def convert_to_json(conv: Conversation):
    def serialize_conversation(conversation):
        return {
            "id": conversation.id,
            "name": conversation.name,
            "model": str(conversation.model),
            "responses": [serialize_response(r) for r in conversation.responses],
        }

    def serialize_response(response):
        res = {
            "prompt": serialize_prompt(response.prompt),
            "chunks": response._chunks,
            "done": response._done,
            "start": timestamp_to_iso(response._start),
            "end": timestamp_to_iso(response._end),
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }

        if response.conversation and response.conversation.id != conv.id:
            res["conversation"] = serialize_conversation(response.conversation)

        return res

    def serialize_prompt(prompt):
        if not prompt:
            return None
        return {
            "prompt": prompt.prompt,
            "system": prompt.system,
            "model": str(prompt.model),
            "options": vars(prompt.options) if prompt.options else {},
        }

    def timestamp_to_iso(ts):
        if not ts:
            return None
        return datetime.fromtimestamp(ts).isoformat()

    return serialize_conversation(conv)


def print_json(conversation: Conversation, filename: str):
    json_data = convert_to_json(conversation)
    with open(filename, "w") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        f.write("\n")
