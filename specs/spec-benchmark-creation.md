# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- create a benchmark to test different prompts and models using python, ollama, and API

## Mid-Level Objective

- create a CLI application that accept a yaml file and run the tests based on it's content
- run each prompt for each model and register the time of execution, token inputs, token outputs, power consumption, price and if it passed the test or not
- output in the terminal
- output a table reporting the details of each evaluation
- output a summary:
  - for the model: total time, total cost, total input and output tokens, total power consumption, percentage of success
  - for the prompt: percentage of success for each model, percentage of success across all models, average token input (should be the same everywhere), average token output, average cost, average time, average power consumption

## Implementation Notes
- No need to import any external libraries see pyproject.toml for dependencies.
- Comment every function.
- For typer commands add usage examples starting with `uv run main <func name dash sep and params>`
- When code block is given in low-level tasks, use it without making changes (Task 4).
- Carefully review each low-level task for exact code changes.

## Context

### Beginning context
- `pyproject.toml` (readonly)

### Ending context
- `pyproject.toml` (readonly)
- `src/main.py` (new file)
- `src/model_list.py` (new file)
- `src/load_file.py` (new file)
- `src/output.py` (new file)
- `src/call_llm.py` (new file)
- `src/evaluate.py` (new file)
- `src/data_types.py` (new file)


## Low-Level Tasks
> Ordered from start to finish

1. Create our data types
```aider
CREATE src/data_types.py
    CREATE pydantic types:

        CREATE PromptTest(BaseModel): {prompt: str, output: str, test_method: Literal["exact"]}

        CREATE LLMModel(BaseModel): {
            provider: Literal["OpenAI", "Anthropic", "Ollama"],
            model_name: str,
            input_price: float,
            output_price: float,
            parameter_number: float
        }

        CREATE LLMOuptput(BaseModel): {
            prompt: PromptTest,
            model: LLMModel,
            input_tokens: int,
            output_tokens: int,
            response: str
        }

        CREATE TestResult(BaseModel): {
            prompt: PromptTest,
            model: LLMModel,
            passed: Boolean,
            input_tokens: int,
            output_tokens: int,
            inference_time: TimeDelta,
            power_consumption: float
        }

        CREATE Benchmark(BaseModel): {
            models: List[LLMModel],
            prompts: List[PromptTest]
        }
```
2. CREATE src/model_list.py
```aider
CREATE src/model_list.py
    CREATE a dict for each provider, with the name as key and LLMModel as value.
    openai = {"gpt-4o": {name:"gpt-4o", input:2.5, output:10, parameter:200}}
    anthropic = {"sonnet 3.5": {name:"claude-3-5-sonnet-20241022", input:3, output:15, parameter:175}}
    Ollama = {"qwen2.5-coder": {name:"qwen2.5-coder:7b", input:0, output:0, parameter:7}}
```

3. CREATE src/load_file.py
```aider
CREATE src/load_file.py
    CREATE def load_from_yaml(file_path: str) -> Benchmark:
        example yaml file:
        ```yaml
models:
  - openai:gpt-4o
  - anthropic:sonnet 3.5
  - ollama:qwen2.5-coder
  - <provider>:<name>

prompts:
  - test_1:
    prompt: "the prompt to be tested here"
    output: "the expected output here / elements needed to evaluate the model here"
    method: "evaluation_method"
  - another_test:
    prompt: "the prompt to be tested here"
    output: "the expected output here / elements needed to evaluate the model here"
    method: "exact"
        ```
        use the src/model_list.py to load the relevant model with all the necessary informations

```

4. CREATE .env.example
```aider
CREATE .env.example
need OPENAI_KEY, ANTHROPIC_KEY
```

5. CREATE src/call_llm.py
```aider
CREATE src/call_llm.py

    CREATE def call_llm(model: LLMModel, prompt: PromptTest) -> LLMOutput:
        based on the provider, make the inference in a specific way

    CREATE def call_openai(model: LLMModel, prompt: PromptTest) -> LLMOutput:
    ```python
from openai import OpenAI

client = OpenAI(api_key="your api key here")
completion = client.chat.completions.create(
model="gpt-4o",
messages=[
    {"role": "user", "content": <input prompt here>}
])
message_content = completion.choices[0].message.content
input_tokens = completion.usage.prompt_tokens
output_tokens = completion.usage.completion_tokens
    ```
    load the api_key from .env file
```

6. MODIFY src/call_llm.py
```aider
MODIFY src/call_llm.py
    MIRROR call_openai: CREATE def call_anthropic(model:LLMModel, prompt:PromptTest) -> LLMOutput:
    ```python
from anthropic import Anthropic

client = Anthropic(api_key="your_api_key_here")
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[
        {"role": "user", "content": "Write a haiku about recursion in programming."}
    ]
)
message_content = response.content[0].text
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
```
    load the api_key from .env file


7. MODIFY src/call_llm.py
```aider
MODIFY src/call_llm.py
    MIRROR call_openai: CREATE def call_ollama(model:LLMModel, prompt:PromptTest) -> LLMOutput:
    ```python
import ollama

response = ollama.chat(
    model='llama2',
    messages=[
        {"role": "user", "content": "Write a haiku about programming."}
    ]
)
message_content = response['message']['content']
print(message_content)

def estimate_input_tokens(prompt):
    # for more precise input token, we need to use a model-specific tokenizer, which is not provider yet
    return len(prompt) // 4  # Approximately 1 token per 4 characters
output_tokens = response['eval_count']
    ```
    load the api_key from .env file
```

8. CREATE src/evaluate.py
```aider
    CREATE def estimate_power_consumption(tokens_output: int, parameters: int) -> float
    # output is in Wh, source https://ecologits.ai/latest/methodology/llm_inference/
    # it's a first approximation, see paper for full detail
    return tokens_output * ((8.91e - 5) * parameters + 1.43e - 3)

    CREATE def test_prompt(prompt:PromptTest, output: str) -> boolean:
    test if output pass the test or not. have a test method for each test

    CREATE def test_prompt_exact(prompt:PromptTest, output: str) -> boolean
    return true if output is exactly equals to prompt.prompt

    CREATE def evaluate(model:LLMModel, prompt:PromptTest) -> TestResult
    time the execution of call_llm(model, prompt)
    compute the power_consumption
    evaluate if prompt pass the test using test_prompt

```

9. CREATE src/output.py
```aider
CREATE src/output.py
    CREATE def print_to_str(results: List[TestResult]) -> str:
    - output a table reporting the details of each evaluation
    - output a summary:
      - for each model: total time, total cost, total input and output tokens, total power consumption, percentage of success
      - for each prompt: percentage of success for each model, percentage of success across all models, average token input (should be the same everywhere), average token output, average cost, average time, average power consumption
```

10. CREATE src/main.py
```aider
CREATE src/main.py
    accept 1 argument as a CLI, which is a str representing the path to a file
    load the models, load the prompts
    run the tests, for each model then for each prompt. Do this in this order because loading a model in memory might take up some time and resources, so it's best to do all the prompts for one model then change model than doing the opposite
    output the results
```
