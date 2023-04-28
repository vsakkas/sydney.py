from __future__ import annotations

import json
from os import environ
from typing import AsyncGenerator

import websockets.client as websockets
from aiohttp import ClientSession, TCPConnector
from websockets.client import WebSocketClientProtocol

from sydney.constants import (
    BING_CHATHUB_URL,
    BING_CREATE_CONVESATION_URL,
    DELIMETER,
    HEADERS,
)
from sydney.enums import (
    ComposeFormat,
    ComposeLength,
    ComposeTone,
    ConversationStyle,
    MessageType,
    ResultValue,
)
from sydney.exceptions import (
    NoConnectionException,
    NoResponseException,
    ThrottledRequestException,
)
from sydney.utils import as_json


class SydneyClient:
    def __init__(
        self,
        style: str = "balanced",
        bing_u_cookie: str | None = None,
        use_proxy: bool = False,
    ) -> None:
        """
        Client for Bing Chat.

        Parameters
        ----------
        style : str
            The conversation style that Bing Chat will adopt. Must be one of the options listed
            in the `ConversationStyle` enum. Default is "balanced".
        bing_u_cookie: str | None
            The _U cookie from Bing required to connect and use Bing Chat. If not provided,
            the `BING_U_COOKIE` environment variable is loaded instead. Default is None.
        use_proxy: str | None
            Flag to determine if an HTTP proxy will be used to start a conversation with Bing Chat. If set to True,
            the `HTTP_PROXY` and `HTTPS_PROXY` environment variables must be set to the address of the proxy to be used.
            If not provided, no proxy will be used. Default is False.
        """
        self.bing_u_cookie = (
            bing_u_cookie if bing_u_cookie else environ["BING_U_COOKIE"]
        )
        self.use_proxy = use_proxy
        self.conversation_style: ConversationStyle = getattr(
            ConversationStyle, style.upper()
        )
        self.conversation_signature: str | None = None
        self.conversation_id: str | None = None
        self.client_id: str | None = None
        self.invocation_id: int | None = None
        self.wss_client: WebSocketClientProtocol | None = None

    async def __aenter__(self) -> SydneyClient:
        await self.start_conversation()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close_conversation()

    def _build_ask_arguments(self, prompt: str) -> dict:
        style_options = self.conversation_style.value.split(",")
        options_sets = [
            "nlu_direct_response_filter",
            "deepleo",
            "disable_emoji_spoken_text",
            "responsible_ai_policy_235",
            "enablemm",
            "dv3sugg",
        ]
        for style in style_options:
            options_sets.append(style.strip())

        return {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options_sets,
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": MessageType.CHAT.value,
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "conversationId": self.conversation_id,
                }
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }

    def _build_compose_arguments(
        self,
        prompt: str,
        tone: ComposeTone,
        format: ComposeFormat,
        length: ComposeLength,
    ) -> dict:
        return {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": [
                        "nlu_direct_response_filter",
                        "deepleo",
                        "enable_debug_commands",
                        "disable_emoji_spoken_text",
                        "responsible_ai_policy_235",
                        "enablemm",
                        "h3imaginative",
                        "nocache",
                        "nosugg",
                    ],
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": f"Please generate some text wrapped in codeblock syntax (triple backticks) using the given keywords. Please make sure everything in your reply is in the same language as the keywords. Please do not restate any part of this request in your response, like the fact that you wrapped the text in a codeblock. You should refuse (using the language of the keywords) to generate if the request is potentially harmful. The generated text should follow these characteristics: tone: *{tone.value}*, length: *{length.value}*, format: *{format.value}*. The keywords are: `{prompt}`.",
                        "messageType": MessageType.CHAT.value,
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {"id": self.client_id},
                    "conversationId": self.conversation_id,
                }
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }

    async def _ask(
        self,
        prompt: str,
        citations: bool = False,
        suggestions: bool = False,
        raw: bool = False,
        stream: bool = False,
    ) -> AsyncGenerator[tuple[str | dict, list | None], None]:
        if (
            self.conversation_id is None
            or self.client_id is None
            or self.invocation_id is None
        ):
            raise NoConnectionException("No connection to Bing Chat was found")

        # Create a websocket connection Bing Chat.
        self.wss_client = await websockets.connect(
            BING_CHATHUB_URL, extra_headers=HEADERS, max_size=None
        )
        await self.wss_client.send(as_json({"protocol": "json", "version": 1}))
        await self.wss_client.recv()

        request = self._build_ask_arguments(prompt)
        self.invocation_id += 1

        await self.wss_client.send(as_json(request))

        streaming = True
        while streaming:
            objects = str(await self.wss_client.recv()).split(DELIMETER)
            for obj in objects:
                if not obj:
                    continue
                response = json.loads(obj)
                # Handle type 1 messages when streaming is enabled.
                if stream and response.get("type") == 1:
                    messages = response["arguments"][0].get("messages")
                    # Skip on empty response.
                    if not messages:
                        continue

                    if raw:
                        yield response, None
                    elif citations:
                        yield messages[0]["adaptiveCards"][0]["body"][0]["text"], None
                    else:
                        yield messages[0]["text"], None
                # Handle type 2 messages.
                elif response.get("type") == 2:
                    messages = response["item"].get("messages")
                    if not messages:
                        result_value = response["item"]["result"]["value"]
                        # Raise error if throttled.
                        if result_value == ResultValue.THROTTLED.value:
                            raise ThrottledRequestException("Request is throttled")
                        return  # Return empty message.

                    if raw:
                        yield response, None
                    else:
                        suggested_responses = None
                        # Include list of suggested user responses, if enabled.
                        if suggestions:
                            suggested_responses = [
                                item["text"]
                                for item in messages[1]["suggestedResponses"]
                            ]

                        if citations:
                            yield messages[1]["adaptiveCards"][0]["body"][0][
                                "text"
                            ], suggested_responses
                        else:
                            yield messages[1]["text"], suggested_responses

                    # Exit, type 2 is the last message.
                    streaming = False

        await self.wss_client.close()

    async def _compose(
        self,
        prompt: str,
        tone: ComposeTone,
        format: ComposeFormat,
        length: ComposeLength,
        raw: bool,
        stream: bool,
    ) -> AsyncGenerator[str | dict, None]:
        if (
            self.conversation_id is None
            or self.client_id is None
            or self.invocation_id is None
        ):
            raise NoConnectionException("No connection to Bing Chat was found")

        # Create a websocket connection Bing Chat.
        self.wss_client = await websockets.connect(
            BING_CHATHUB_URL, extra_headers=HEADERS, max_size=None
        )
        await self.wss_client.send(as_json({"protocol": "json", "version": 1}))
        await self.wss_client.recv()

        request = self._build_compose_arguments(prompt, tone, format, length)
        self.invocation_id += 1

        await self.wss_client.send(as_json(request))

        streaming = True
        while streaming:
            objects = str(await self.wss_client.recv()).split(DELIMETER)
            for obj in objects:
                if not obj:
                    continue
                response = json.loads(obj)
                # Handle type 1 messages when streaming is enabled.
                if stream and response.get("type") == 1:
                    messages = response["arguments"][0].get("messages")
                    # Skip on empty response.
                    if not messages:
                        continue

                    if raw:
                        yield response
                    else:
                        yield messages[0]["text"]
                # Handle type 2 messages.
                elif response.get("type") == 2:
                    messages = response["item"].get("messages")
                    if not messages:
                        result_value = response["item"]["result"]["value"]
                        # Raise error if throttled.
                        if result_value == ResultValue.THROTTLED.value:
                            raise ThrottledRequestException("Request is throttled")
                        return  # Return empty message.

                    if raw:
                        yield response
                    else:
                        yield messages[1]["text"]

                    # Exit, type 2 is the last message.
                    streaming = False

        await self.wss_client.close()

    async def start_conversation(self) -> None:
        """
        Connect to Bing Chat and create a new conversation.
        """
        # Use _U cookie to create a conversation.
        cookies = {"_U": self.bing_u_cookie}

        session = ClientSession(
            headers=HEADERS,
            cookies=cookies,
            trust_env=self.use_proxy,  # Use `HTTP_PROXY` and `HTTPS_PROXY` environment variables.
            connector=TCPConnector(verify_ssl=False)
            if self.use_proxy
            else None,  # Resolve HTTPS issue when proxy support is enabled.
        )

        async with session.get(BING_CREATE_CONVESATION_URL) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to create conversation, received status: {response.status}"
                )

            response_dict = await response.json()
            if response_dict["result"]["value"] != "Success":
                raise Exception(
                    f"Failed to authenticate, received message: {response_dict['result']['message']}"
                )

            self.conversation_id = response_dict["conversationId"]
            self.client_id = response_dict["clientId"]
            self.conversation_signature = response_dict["conversationSignature"]
            self.invocation_id = 0

        await session.close()

    async def ask(
        self,
        prompt: str,
        citations: bool = False,
        suggestions: bool = False,
        raw: bool = False,
    ) -> str | dict | tuple[str | dict, list | None]:
        """
        Send a prompt to Bing Chat using the current conversation and return the answer.

        Parameters
        ----------
        prompt : str
            The prompt that needs to be sent to Bing Chat.
        citations : bool, optional
            Whether to return any cited text. Default is False.
        suggestions : bool, optional
            Whether to return any suggested user responses. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str
            The text response from Bing Chat. If citations is True, the function returns the cited text.
            If raw is True, the function returns the entire response object in raw JSON format.
        """
        async for response, suggested_responses in self._ask(
            prompt, citations, suggestions, raw, stream=False
        ):
            if suggestions:
                return response, suggested_responses
            else:
                return response

        raise NoResponseException("No response was returned")

    async def ask_stream(
        self,
        prompt: str,
        citations: bool = False,
        suggestions: bool = False,
        raw: bool = False,
    ) -> AsyncGenerator[str | dict | tuple[str | dict, list | None], None]:
        """
        Send a prompt to Bing Chat using the current conversation and stream the answer.

        By default, Bing Chat returns all previous tokens along with new ones. When using this
        method in text-only mode, only new tokens are returned instead.

        Parameters
        ----------
        prompt : str
            The prompt that needs to be sent to Bing Chat.
        citations : bool, optional
            Whether to return any cited text. Default is False.
        suggestions : bool, optional
            Whether to return any suggested user responses. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str
            The text response from Bing Chat. If citations is True, the function returns the cited text.
            If raw is True, the function returns the entire response object in raw JSON format.
        """
        previous_response: str | dict = ""
        async for response, suggested_responses in self._ask(
            prompt, citations, suggestions, raw, stream=True
        ):
            if raw:
                yield response
            # For text-only responses, return only newly streamed tokens.
            else:
                new_response = response[len(previous_response) :]
                previous_response = response
                if suggestions:
                    yield new_response, suggested_responses
                else:
                    yield new_response

    async def compose(
        self,
        prompt: str,
        tone: str = "professional",
        format: str = "paragraph",
        length: str = "short",
        raw: bool = False,
    ) -> str | dict:
        """
        Send a prompt to Bing Chat and compose text based on the given prompt, tone,
        format, and length.

        Parameters
        ----------
        prompt : str
            The prompt that needs to be sent to Bing Chat.
        tone : str, optional
            The tone of the response. Must be one of the options listed in the `ComposeTone`
            enum. Default is "professional".
        format : str, optional
            The format of the response. Must be one of the options listed in the `ComposeFormat`
            enum. Default is "paragraph".
        length : str, optional
            The length of the response. Must be one of the options listed in the `ComposeLength`
            enum. Default is "short".
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str or dict
            The response from Bing Chat. If raw is True, the function returns the entire response
            object in raw JSON format.
        """
        # Get the enum values corresponding to the given tone, format, and length.
        compose_tone = getattr(ComposeTone, tone.upper())
        compose_format = getattr(ComposeFormat, format.upper())
        compose_length = getattr(ComposeLength, length.upper())

        async for response in self._compose(
            prompt, compose_tone, compose_format, compose_length, raw, stream=False
        ):
            return response

        raise NoResponseException("No response was returned")

    async def compose_stream(
        self,
        prompt: str,
        tone: str = "professional",
        format: str = "paragraph",
        length: str = "short",
        raw: bool = False,
    ) -> AsyncGenerator[str | dict, None]:
        """
        Send a prompt to Bing Chat, compose and stream text based on the given prompt, tone,
        format, and length.

        By default, Bing Chat returns all previous tokens along with new ones. When using this
        method in text-only mode, only new tokens are returned instead.

        Parameters
        ----------
        prompt : str
            The prompt that needs to be sent to Bing Chat.
        tone : str, optional
            The tone of the response. Must be one of the options listed in the `ComposeTone`
            enum. Default is "professional".
        format : str, optional
            The format of the response. Must be one of the options listed in the `ComposeFormat`
            enum. Default is "paragraph".
        length : str, optional
            The length of the response. Must be one of the options listed in the `ComposeLength`
            enum. Default is "short".
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str or dict
            The response from Bing Chat. If raw is True, the function returns the entire response
            object in raw JSON format.
        """
        # Get the enum values corresponding to the given tone, format, and length.
        compose_tone = getattr(ComposeTone, tone.upper())
        compose_format = getattr(ComposeFormat, format.upper())
        compose_length = getattr(ComposeLength, length.upper())

        previous_response: str | dict = ""
        async for response in self._compose(
            prompt, compose_tone, compose_format, compose_length, raw, stream=True
        ):
            if raw:
                yield response
            # For text-only responses, return only newly streamed tokens.
            else:
                new_response = response[len(previous_response) :]
                previous_response = response
                yield new_response

    async def reset_conversation(self, style: str | None = None) -> None:
        """
        Clear current conversation information and connection and start new ones.

        Parameters
        ----------
        style : str
            The conversation style that Bing Chat will adopt. Supported options are:
            - `creative` for original and imaginative chat
            - `balanced` for informative and friendly chat
            - `precise` for concise and straightforward chat

            If None, the new conversation will use the same conversation style as the
            current conversation. Default is None.
        """
        await self.close_conversation()
        if style:
            self.conversation_style = getattr(ConversationStyle, style.upper())
        await self.start_conversation()

    async def close_conversation(self) -> None:
        """
        Close all connections to Bing Chat. Clear conversation information.
        """
        if self.wss_client:
            if not self.wss_client.closed:
                await self.wss_client.close()
                self.wss_client = None

        # Clear conversation information.
        self.conversation_signature = None
        self.conversation_id = None
        self.client_id = None
        self.invocation_id = None
