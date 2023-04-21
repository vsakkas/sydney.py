# Sydney.py

[![Latest Release](https://img.shields.io/github/v/release/vsakkas/sydney.py.svg)](https://github.com/vsakkas/sydney.py/releases/tag/v0.12.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/vsakkas/sydney.py/blob/master/LICENSE)

Python Client for Bing Chat, also known as Sydney.

> **Note**
> This is an **unofficial** client.

## Features

- Connect to Bing Chat, Microsoft's AI-powered personal assistant.
- Ask questions and have a conversation in various conversation styles.
- Compose content in various formats and tones.
- Stream response tokens for real-time communication.
- Retrieve citations and suggested user responses.
- Supports asyncio for efficient and non-blocking I/O operations.

## Requirements

- Python 3.9 or newer
- Microsoft account with access to [Bing Chat](https://bing.com/chat)

## Installation

To install Sydney.py, run the following command:

```bash
pip install sydney-py
```

or, if you use [poetry](https://python-poetry.org/):

```bash
poetry add sydney-py
```

## Usage

### Prerequisites

To use Sydney.py you first need to extract the `_U` cookie from [Bing](https://bing.com). The `_U` cookie is used to authenticate your requests to the Bing Chat API.

To get the `_U` cookie, follow these steps:
- Log in to [Bing](https://bing.com) using your Microsoft account.
- Open the developer tools in your browser (usually by pressing `F12` or right-clicking and selecting `Inspect element`).
- Select the `Storage` tab and click on the `Cookies` option to view all cookies associated with the website.
- Look for the `_U` cookie and click on it to expand its details.
- Copy the value of the `_U` cookie (it should look like a long string of letters and numbers).

Then, set it as an environment variable in your shell:

```bash
export BING_U_COOKIE=<your-cookie>
```

or, in your Python code:

```python
os.environ["BING_U_COOKIE"] = "<your-cookie>"
```

### Example

You can use Sydney.py to easily create a CLI client for Bing Chat:

```python
import asyncio

from sydney import SydneyClient


async def main() -> None:
    async with SydneyClient() as sydney:
        while True:
            prompt = input("You: ")

            if prompt == "!reset":
                await sydney.reset_conversation()
                continue
            elif prompt == "!exit":
                break

            print("Sydney: ", end="", flush=True)
            async for response in sydney.ask_stream(prompt):
                print(response, end="", flush=True)
            print("\n")


if __name__ == "__main__":
    asyncio.run(main())
```

### Sydney Client

You can create a Sydney Client and initialize a connection with Bing Chat which starts a conversation:

```python
sydney = SydneyClient()

await sydney.start_conversation()

# Conversation

await sydney.end_conversation()
```

Alternatively, you can use the `async with` statement to keep the code compact:

```python
async with SydneyClient() as sydney:
    # Conversation
```

### Conversation Style

You can set the conversation style when creating a Sydney Client:

```python
sydney = SydneyClient(style="creative")
```

The available options are `creative`, `balanced` and `precise`.

### Reset Conversation

You can reset the conversation in order to make the client forget the previous conversation. You can also change the conversation style without creating a new client:

```python
async withSydneyClient() as sydney:
    # Conversation
    await sydney.reset_conversation(style="creative")
```

### Ask

You can ask Bing Chat questions and (optionally) include citations in the results:

```python
async with SydneyClient() as sydney:
    response = await sydney.ask("When was Bing Chat released?", citations=True)
    print(response)
```

You can also stream the response tokens:

```python
async with SydneyClient() as sydney:
    async for response in sydney.ask_stream("When was Bing Chat released?", citations=True):
        print(response, end="", flush=True)
```

Both versions of the `ask` method support the same parameters.

### Compose

You can ask Bing Chat to compose different types of content, such emails, articles, ideas and more:

```python
async with SydneyClient() as sydney:
    response = sydney.compose("Why Python is a great language", format="ideas")
    print(response)
```

You can also stream the response tokens:

```python
async with SydneyClient() as sydney:
   async for response in sydney.compose_stream("Why Python is a great language", format="ideas"):
        print(response, end="", flush=True)
```

The available options for the `tone` parameter are:
- `professional`
- `casual`
- `enthusiastic`
- `informational`
- `funny`

The available options for the `format` parameter are:
- `paragraph`
- `email`
- `blogpost`
- `ideas`

The available options for the `length` parameter are:
- `short`
- `medium`
- `long`

Both versions of the `compose` method support the same parameters.

### Suggested Responses

You can also receive the suggested user responses as generated by Bing Chat along with the text answer. Both `ask` and `ask_stream` support this feature:

```python
async with SydneyClient() as sydney:
    response, suggested_responses = await sydney.ask(prompt, suggestions=True)
    if suggested_responses:
        print("Suggestions:")
        for suggestion in suggested_responses:
            print(suggestion)
```

> **Note**
> The suggested user responses are returned only if the suggestions parameter is true. Otherwise, the `ask` and `ask_stream` methods return only the response.

> **Note**
> When using the `ask_stream` method with the suggestions parameter, only the suggested user responses returned lastly may contain a value. For all previous iterations, the suggested user responses will be `None`.

### Raw Response

You can also receive the raw JSON response that comes from Bing Chat instead of a text answer. Both `ask` and `compose` support this feature:

```python
async with SydneyClient() as sydney:
    response = await sydney.ask("When was Bing Chat released?", raw=True)
    print(response)
```

*For more detailed documentation and options, please refer to the code docstrings.*

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsakkas/sydney.py/blob/master/LICENSE) file for details.
