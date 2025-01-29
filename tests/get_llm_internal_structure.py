import json
import dataclasses
import llm

def conversation_to_dict(obj, visited=None, depth=0):
    """Convert conversation object and its nested objects to a dictionary."""
    # Limit recursion depth
    if depth > 100:  # arbitrary limit to prevent stack overflow
        return "MAX_DEPTH_REACHED"
    
    if visited is None:
        visited = set()

    # Handle None and primitive types
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Get object id to track visited objects
    obj_id = id(obj)
    if obj_id in visited:
        return "CIRCULAR_REFERENCE"
    visited.add(obj_id)

    try:
        if dataclasses.is_dataclass(obj):
            return {k: conversation_to_dict(v, visited, depth + 1) 
                   for k, v in dataclasses.asdict(obj).items()}
        elif isinstance(obj, (list, tuple)):
            return [conversation_to_dict(x, visited, depth + 1) for x in obj]
        elif isinstance(obj, dict):
            return {str(k): conversation_to_dict(v, visited, depth + 1) 
                   for k, v in obj.items()}
        elif hasattr(obj, '__dict__'):
            return {k: conversation_to_dict(v, visited, depth + 1) 
                   for k, v in vars(obj).items() 
                   if not k.startswith('_')}  # Skip private attributes
        # Handle other types that might be problematic
        elif hasattr(obj, '__slots__'):
            return {slot: conversation_to_dict(getattr(obj, slot), visited, depth + 1) 
                   for slot in obj.__slots__ 
                   if hasattr(obj, slot)}
        # Convert any other type to string
        return str(obj)
    finally:
        visited.remove(obj_id)

model = llm.get_model("deepseek-chat")
conversation = model.conversation()


def run():
    response = conversation.prompt(
        "change the gretting to be more casual",
        system='Act as an expert software developer.\nTake requests for changes to the supplied code.\nIf the request is ambiguous, ask questions.\n\nAlways reply to the user in the same language they are using.\n\n\nOnce you understand the request you MUST:\n1. Determine if any code changes are needed.\n2. Explain any needed changes.\n3. If changes are needed, output a copy of each file that needs changes.\n\nTo suggest changes to a file you MUST return the entire content of the updated file.\nYou MUST use this *file listing* format:\n\npath/to/filename.js\n```\n// entire file content ...\n// ... goes in between\n```\n\nEvery *file listing* MUST use this format:\n- First line: the filename with any originally provided path; no extra markup, punctuation, comments, etc. **JUST** the filename with path.\n- Second line: opening ```\n- ... entire content of the file ...\n- Final line: closing ```\n\nTo suggest changes to a file you MUST return a *file listing* that contains the entire content of the file.\n*NEVER* skip, omit or elide content from a *file listing* using "..." or by adding comments like "... rest of code..."!\nCreate a new file you MUST return a *file listing* which includes an appropriate filename, including any appropriate path.\n\n\n',
    )
    print(response.text())

    response2 = conversation.prompt(
        "I switched to a new code base. Please don't consider the above files or try to edit them any longer."
    )
    print(response2.text())

    response3 = conversation.prompt(
        "Here are summaries of some files present in my git repository.\nDo not propose changes to these files, treat them as *read-only*.\nIf you need to edit any of these files, ask me to *add them to the chat* first.\n\n.gitignore\n\n.python-version\n\nREADME.md\n\npyproject.toml\n\nspecs/spec-benchmark-creation.md\n\nspecs/spec-benchmark-creation_v0.md\n\nsrc/serve_prompt_capture.py\n\nuv.lock\n"
    )
    for chunk in response3:
        print(chunk, end="")

    # Save conversation to JSON file
    with open(f"test_conversation_{conversation.id}.json", "w") as f:
        json.dump(conversation_to_dict(conversation), f, indent=2, default=str)
    print(conversation)


run()
