MODIFY src/serve_prompt_capture.py

    1. add def generate_conversation(request: JSON) -> Conversation:

```python
import llm

model = llm.get_model()
conversation: Conversation = model.conversation()
```

    2. modify generate_conversation:
    the request object will look like what's provided in <json_example>. I want you to modify the `conversation` object to include the `messages` in the conversation, like it already happen.
    You can find relevant information about the code structure of the `conversation` object in <code_structure>.

<json_example>

````json
{
  "messages": [
    {
      "role": "system",
      "content": "Act as an expert code analyst.\nAnswer questions about the supplied code.\nAlways reply to the user in the same language they are using.\n\nDescribe code changes however you like. Don't use SEARCH/REPLACE blocks!\n"
    },
    {
      "role": "user",
      "content": "I am working with you on code in a git repository.\nHere are summaries of some files present in my git repo.\nIf you need to see the full contents of any files to answer my questions, ask me to *add them to the chat*.\n\n.gitignore\n\n.python-version\n\nREADME.md\n\npyproject.toml\n\nspecs/spec-benchmark-creation.md\n\nspecs/spec-benchmark-creation_v0.md\n\nsrc/serve_prompt_capture.py\n\nuv.lock\n"
    },
    {
      "role": "assistant",
      "content": "Ok, I won't try and edit those files without asking first."
    },
    {
      "role": "user",
      "content": "I am not sharing the full contents of any files with you yet."
    },
    {
      "role": "assistant",
      "content": "Ok."
    },
    {
      "role": "user",
      "content": "this is a test. It might return an error\n\n"
    }
  ],
  "model": "TestModelName",
  "stream": true,
  "temperature": 0
}

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
      "content": "this is another stuff\n\nTo suggest changes to a file you MUST return the entire content of the updated file.\nYou MUST use this *file listing* format:\n\npath/to/filename.js\n```\n// entire file content ...\n// ... goes in between\n```\n\nEvery *file listing* MUST use this format:\n- First line: the filename with any originally provided path; no extra markup, punctuation, comments, etc. **JUST** the filename with path.\n- Second line: opening ```\n- ... entire content of the file ...\n- Final line: closing ```\n\nTo suggest changes to a file you MUST return a *file listing* that contains the entire content of the file.\n*NEVER* skip, omit or elide content from a *file listing* using \"...\" or by adding comments like \"... rest of code...\"!\nCreate a new file you MUST return a *file listing* which includes an appropriate filename, including any appropriate path.\n\n\n"
    }
  ],
  "model": "TestModelName",
  "stream": true,
  "temperature": 0
}
````

</json_example>

<code_structure>

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

</code_structure>
