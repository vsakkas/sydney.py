import json
import os

import websockets.client as websockets
from aiohttp import ClientSession

from .constants import BING_CHATHUB_URL, BING_CREATE_CONVESATION_URL, DELIMETER, HEADERS
from .enums import ConversationStyle
from .utils import as_json


class SydneyClient:
    def __init__(self) -> None:
        self.conversation_id: str = None
        self.client_id: str = None
        self.conversation_signature: str = None
        self.invocation_id: str = None
        self.conversation_style: ConversationStyle = None
        self.wss_client = None

    def _build_request_arguments(self, prompt: str) -> dict:
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
                        self.conversation_style.value,
                    ],
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": "Chat",
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

    async def _ask(
        self,
        prompt: str,
        citations: bool = False,
        raw: bool = False,
        stream: bool = False,
    ) -> str | dict:
        # Create a connection Bing Chat.
        self.wss_client = await websockets.connect(
            BING_CHATHUB_URL, extra_headers=HEADERS, max_size=None
        )
        await self.wss_client.send(as_json({"protocol": "json", "version": 1}))
        await self.wss_client.recv()

        request = self._build_request_arguments(prompt)
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
                if (
                    stream
                    and response.get("type") == 1
                    and response["arguments"][0].get("messages")
                ):
                    if raw:
                        yield response
                    elif citations:
                        yield response["arguments"][0]["messages"][0]["adaptiveCards"][0]["body"][0]["text"]
                    else:
                        yield response["arguments"][0]["messages"][0]["text"]
                # Handle type 2 messages.
                elif response.get("type") == 2:
                    if raw:
                        yield response
                    if citations:
                        yield response["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
                    yield response["item"]["messages"][1]["text"]

                    # Exit, type 2 is the last message.
                    streaming = False

        await self.wss_client.close()

    async def start_conversation(self, style: str = "balanced") -> None:
        """
        Connect to Bing Chat and create a new conversation.

        Parameters
        ----------
        style : str
            The conversation style that Bing Chat will adopt. Supported options are:
            - `creative` for original and imaginative chat
            - `balanced` for informative and friendly chat
            - `precise` for concise and straightforward chat

            Default is "balanced".
        """
        # Use _U cookie to create a conversation.
        cookies = {"_U": os.environ["BING_U_COOKIE"]}

        session = ClientSession(headers=HEADERS, cookies=cookies)
        async with session.get(BING_CREATE_CONVESATION_URL) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to create conversation, received status: {response.status}"
                )

            response_dict = await response.json()
            if response_dict["result"]["value"] != "Success":
                raise Exception(
                    f"Failed to authenticate, received message: {response_dict['response']['message']}"
                )

            self.conversation_id = response_dict["conversationId"]
            self.client_id = response_dict["clientId"]
            self.conversation_signature = response_dict["conversationSignature"]
            self.invocation_id = 0
            self.conversation_style = getattr(ConversationStyle, style)

        await session.close()

    async def ask(
        self,
        prompt: str,
        citations: bool = False,
        raw: bool = False,
    ) -> str | dict:
        """
        Send a prompt to Bing Chat using the current conversation and return the answer.

        Parameters
        ----------
        prompt : str
            The prompt that needs to be sent to Bing Chat.
        citations : bool, optional
            Whether to return any cited text. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str
            The text response from Bing Chat. If citations is True, the function returns the cited text.
            If raw is True, the function returns the entire response object in raw JSON format.
        """
        async for response in self._ask(prompt, citations, raw, stream=False):
            return response

    async def ask_stream(
        self,
        prompt: str,
        citations: bool = False,
        raw: bool = False,
    ) -> str | dict:
        """
        Send a prompt to Bing Chat using the current conversation and stream the answer.

        Parameters
        ----------
        prompt : str
            The prompt that needs to be sent to Bing Chat.
        citations : bool, optional
            Whether to return any cited text. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str
            The text response from Bing Chat. If citations is True, the function returns the cited text.
            If raw is True, the function returns the entire response object in raw JSON format.
        """
        async for response in self._ask(prompt, citations, raw, stream=True):
            yield response

    async def reset_conversation(self, style: str = None) -> None:
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
            current conversation.

            Default is None.
        """
        new_style = style if style else self.conversation_style.name

        await self.close_conversation()
        await self.start_conversation(style=new_style)

    async def close_conversation(self) -> None:
        """
        Close all connections to Bing Chat. Clear conversation information.
        """
        if self.wss_client:
            if not self.wss_client.closed:
                await self.wss_client.close()
                self.wss_client = None

        # Clear conversation information.
        self.conversation_id = None
        self.client_id = None
        self.conversation_signature = None
        self.invocation_id = None
        self.conversation_style = None
