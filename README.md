# Sydney.py

[![Latest Release](https://img.shields.io/github/v/release/vsakkas/sydney.py.svg)](https://github.com/vsakkas/sydney.py/releases/tag/v0.10.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/vsakkas/sydney.py/blob/master/LICENSE)

Python Client for Bing Chat, also known as Sydney.

> **Note**
> This is an **unofficial** client.

## Requirements

- Python 3.10 or newer
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

To use Sydney.py you first need to extract the `_U` cookie from [Bing](https://bing.com).

Then, set it as an environment variable in your shell:

```bash
export BING_U_COOKIE=<your-cookie>
```

or, in your Python code:

```python
os.environ["BING_U_COOKIE"] = "<your-cookie>"
```

### Example

You can Sydney.py to easily create a CLI client for Bing Chat:

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
    response = sydney.ask("When was Bing Chat released?", citations=True)
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

Both versions of the `compose` method support parameters for setting the tone, format and length of the composed text.

### Raw Response

You can also receive the raw JSON response that comes from Bing Chat instead of a text answer. Both `ask` and `compose` support this feature:

```python
async with SydneyClient() as sydney:
    response = sydney.ask("When was Bing Chat released?", raw=True)
    print(response)
```

*For more detailed documentation and options, please refer to the code docstrings.*

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsakkas/sydney.py/blob/master/LICENSE) file for details.
