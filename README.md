# Sydney.py

[![Latest Release](https://img.shields.io/github/v/release/vsakkas/sydney.py.svg)](https://github.com/vsakkas/sydney.py/releases/tag/v0.7.0)
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

To use Sydney.py you first need to extract the `_U` cookie from [Bing](https://bing.com).

Then, set it as an environment variable:

```bash
export BING_U_COOKIE=<your-cookie>
```

Then, you can use the provided Sydney Client:

```python
import asyncio

from sydney import SydneyClient


async def main() -> None:
    sydney = SydneyClient()

    await sydney.start_conversation(style="balanced")

    response = await sydney.ask("Hello, how are you?")
    print(response)

    await sydney.reset_conversation()

    prompt = "What's today's weather forecast?"
    async for response in sydney.ask_stream(prompt, citations=True):
        print(response, end="", flush=True)

    await sydney.close_conversation()


if __name__ == "__main__":
    asyncio.run(main())
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsakkas/sydney.py/blob/master/LICENSE) file for details.
