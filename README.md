# <img src="https://raw.githubusercontent.com/vsakkas/sydney.py/master/images/logo.svg" width="28px" /> Sydney.py

[![Latest Release](https://img.shields.io/github/v/release/vsakkas/sydney.py.svg)](https://github.com/vsakkas/sydney.py/releases/tag/v0.18.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/vsakkas/sydney.py/blob/master/LICENSE)

Python Client for Copilot (formerly named Bing Chat), also known as Sydney.

> [!NOTE]
> This is an **unofficial** client.

## Features

- Connect to Copilot, Microsoft's AI-powered personal assistant.
- Ask questions and have a conversation in various conversation styles.
- Compose content in various formats and tones.
- Stream response tokens for real-time communication.
- Retrieve citations and suggested user responses.
- Enhance your prompts with images for an enriched experience.
- Use asyncio for efficient and non-blocking I/O operations.

## Requirements

- Python 3.9 or newer
- Microsoft account with access to [Copilot](https://copilot.microsoft.com/) *(optional)*

## Installation

To install Sydney.py, run the following command:

```bash
pip install sydney-py
```

or, if you use [poetry](https://python-poetry.org/):

```bash
poetry add sydney-py
```

> [!TIP]
> Make sure you're using the latest version of Sydney.py to ensure best compatibility with Copilot.

## Usage

### Prerequisites

To use Sydney.py, you first need to extract all the cookies from the Copilot web page. These cookies are used to authenticate your requests to the Copilot API.

To get the cookies, follow these steps on Microsoft Edge:
- Go to the [Copilot web page](https://copilot.microsoft.com/).
- Open the developer tools in your browser (usually by pressing `F12` or right-clicking on the chat dialog and selecting `Inspect`).
- Select the `Network` tab to view all requests sent to Copilot.
- Write a message on the chat dialog that appears on the web page.
- Find a request named `create?bundleVersion=XYZ` and click on it.
- Scroll down to the requests headers section and copy the entire value after the `Cookie:` field.

Then, set it as an environment variable in your shell:

```bash
export BING_COOKIES=<your-cookies>
```

or, in your Python code:

```python
os.environ["BING_COOKIES"] = "<your-cookies>"
```

> [!TIP]
> In some regions, using cookies is not required, in which case the above instructions can be skipped.

> [!IMPORTANT]
> For regions where a cookie is required, it is recommended to manually write messages to Copilot until a box containing a `Verifying` message appears, which should then switch to a `Success!` message. Without this step, it is possible that Sydney.py will fail with a `CaptchaChallenge` error.

### Example

You can use Sydney.py to easily create a CLI client for Copilot:

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

You can create a Sydney Client and initialize a connection with Copilot which starts a conversation:

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
async with SydneyClient() as sydney:
    # Conversation
    await sydney.reset_conversation(style="creative")
```

### Ask

You can ask Copilot questions and (optionally) include citations in the results:

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


### Attachment

It is also possible to provide a URL to an image as an attachment, which will be used as input together with the prompt:

```python
async with SydneyClient() as sydney:
    response = await sydney.ask("What does this picture show?", attachment="<image-url>")
    print(response)
```


### Web Context

You can also provide the contents of a web page as additional context to be used along with the prompt:

```python
async with SydneyClient() as sydney:
    response = await sydney.ask("Describe the webpage", context="<web-page-source>")
    print(response)
```

### Compose

You can ask Copilot to compose different types of content, such emails, articles, ideas and more:

```python
async with SydneyClient() as sydney:
    response = await sydney.compose("Why Python is a great language", format="ideas")
    print(response)
```

You can also stream the response tokens:

```python
async with SydneyClient() as sydney:
   async for response in sydney.compose_stream("Why Python is a great language", format="ideas"):
        print(response, end="", flush=True)
```

The default available options for the `tone` parameter are:
- `professional`
- `casual`
- `enthusiastic`
- `informational`
- `funny`

It is also possible to provide any other value for the `tone` parameter.

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

You can also receive the suggested user responses as generated by Copilot along with the text answer. Both `ask`, `ask_stream` support this feature:

```python
async with SydneyClient() as sydney:
    response, suggested_responses = await sydney.ask("When was Bing Chat released?", suggestions=True)
    if suggested_responses:
        print("Suggestions:")
        for suggestion in suggested_responses:
            print(suggestion)
```

And also `compose` and `compose_stream`:

```python
async with SydneyClient() as sydney:
    response, suggested_responses = await sydney.compose(
        "Why Python is a great language", format="ideas", suggestions=True
    )
    if suggested_responses:
        print("Suggestions:")
        for suggestion in suggested_responses:
            print(suggestion)
```

> [!NOTE]
> The suggested user responses are returned only if the suggestions parameter is true. Otherwise, all `ask` and `compose` methods return only the response.

> [!NOTE]
> When using the `ask_stream` or `compose_stream` method with the suggestions parameter, only the lastly returned suggested user responses may contain a value. For all previous iterations, the suggested user responses will be `None`.

### Compose using Suggestions

You can also improve or alter the results of `compose` by using either the suggested responses or any other prompt:

```python
async with SydneyClient() as sydney:
    response, suggested_responses = await sydney.compose(
        prompt="Why Python is a great language", format="ideas", suggestions=True,
    )

    response, suggested_responses = await sydney.compose(
        prompt=suggested_responses[0], format="ideas", suggestions=True
    )

    print(response)
```

### Raw Response

You can also receive the raw JSON response that comes from Copilot instead of a text answer. Both `ask` and `compose` support this feature:

```python
async with SydneyClient() as sydney:
    response = await sydney.ask("When was Bing Chat released?", raw=True)
    print(response)
```

### Conversations

You can also receive all existing conversations that were made with the current client:

```python
async with SydneyClient() as sydney:
    response = await sydney.get_conversations()
    print(response)
```

### Exceptions

When something goes wrong, Sydney.py might throw one of the following exceptions:

| Exception                     | Meaning                                   | Solution                |
|-------------------------------|-------------------------------------------|-------------------------|
| `NoConnectionException`       | No connection to Copilot was found        | Retry                   |
| `ConnectionTimeoutException`  | Attempt to connect to Copilot timed out   | Retry                   |
| `NoResponseException`         | No response was returned from Copilot     | Retry or use new cookie |
| `ThrottledRequestException`   | Request is throttled                      | Wait and retry          |
| `CaptchaChallengeException`   | Captcha challenge must be solved          | Use new cookie          |
| `ConversationLimitException`  | Reached conversation limit of N messages  | Start new conversation  |
| `CreateConversationException` | Failed to create conversation             | Retry or use new cookie |
| `GetConversationsException`   | Failed to get conversations               | Retry                   |

*For more detailed documentation and options, please refer to the code docstrings.*

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsakkas/sydney.py/blob/master/LICENSE) file for details.
