from __future__ import annotations

import json
import urllib.parse
from os import getenv
from typing import AsyncGenerator

import websockets.client as websockets
from aiohttp import ClientSession, TCPConnector
from websockets.client import WebSocketClientProtocol

from sydney.constants import (
    BING_CHATHUB_URL,
    BING_CREATE_CONVERSATION_URL,
    BING_GET_CONVERSATIONS_URL,
    BING_KBLOB_URL,
    BING_BLOB_URL,
    DELIMETER,
    CHAT_HEADERS,
    KBLOB_HEADERS,
)
from sydney.enums import (
    ComposeFormat,
    ComposeLength,
    ComposeTone,
    ConversationStyle,
    ConversationStyleOptionSets,
    CustomComposeTone,
    MessageType,
    ResultValue,
)
from sydney.exceptions import (
    CaptchaChallengeException,
    CreateConversationException,
    ConversationLimitException,
    GetConversationsException,
    ImageUploadException,
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
        self.bing_u_cookie = bing_u_cookie if bing_u_cookie else getenv("BING_U_COOKIE")
        self.use_proxy = use_proxy
        self.conversation_style: ConversationStyle = getattr(
            ConversationStyle, style.upper()
        )
        self.conversation_style_option_sets: ConversationStyleOptionSets = getattr(
            ConversationStyleOptionSets, style.upper()
        )
        self.conversation_signature: str | None = None
        self.encrypted_conversation_signature: str | None = None
        self.conversation_id: str | None = None
        self.client_id: str | None = None
        self.invocation_id: int | None = None
        self.number_of_messages: int | None = None
        self.max_messages: int | None = None
        self.wss_client: WebSocketClientProtocol | None = None
        self.session: ClientSession | None = None

    async def __aenter__(self) -> SydneyClient:
        await self.start_conversation()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close_conversation()

    async def _get_session(self, force_close: bool = False) -> ClientSession:
        # Use _U cookie to create a conversation.
        cookies = {"_U": self.bing_u_cookie} if self.bing_u_cookie else {}

        if self.session and force_close:
            await self.session.close()

        if not self.session:
            self.session = ClientSession(
                headers=CHAT_HEADERS,
                cookies=cookies,
                trust_env=self.use_proxy,  # Use `HTTP_PROXY` and `HTTPS_PROXY` environment variables.
                connector=TCPConnector(verify_ssl=False)
                if self.use_proxy
                else None,  # Resolve HTTPS issue when proxy support is enabled.
            )

        return self.session

    def _build_ask_arguments(
        self,
        prompt: str,
        attachment_info: dict | None = None,
        context: str | None = None,
    ) -> dict:
        style_options = self.conversation_style_option_sets.value.split(",")
        options_sets = [
            "nlu_direct_response_filter",
            "deepleo",
            "disable_emoji_spoken_text",
            "responsible_ai_policy_235",
            "enablemm",
            "dv3sugg",
            "autosave",
            "iyxapbing",
            "iycapbing",
            "galileo",
            "saharagenconv5",
            "eredirecturl",
            "logprobsc",
            "bof108t525",
            "cacheclean",
        ]
        for style in style_options:
            options_sets.append(style.strip())

        image_url, original_image_url = None, None
        if attachment_info:
            image_url = BING_BLOB_URL + attachment_info["blobId"]
            original_image_url = BING_BLOB_URL + attachment_info["blobId"]

        return {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options_sets,
                    "conversationHistoryOptionsSets": [
                        "autosave",
                        "savemem",
                        "uprofupd",
                        "uprofgen",
                    ],
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": MessageType.CHAT.value,
                        "imageUrl": image_url,
                        "originalImageUrl": original_image_url,
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "tone": str(self.conversation_style.value),
                    "conversationId": self.conversation_id,
                    "previousMessages": [  # Conditionally include this field
                        {
                            "author": "user",
                            "description": context,
                            "contextType": "WebPage",
                            "messageType": "Context",
                        }
                    ]
                    if context
                    else None,
                }
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }

    def _build_compose_arguments(
        self,
        prompt: str,
        tone: ComposeTone | CustomComposeTone,
        format: ComposeFormat,
        length: ComposeLength,
    ) -> dict:
        return {
            "arguments": [
                {
                    "source": "edge_coauthor_prod",
                    "optionsSets": [
                        "nlu_direct_response_filter",
                        "deepleo",
                        "enable_debug_commands",
                        "disable_emoji_spoken_text",
                        "responsible_ai_policy_235",
                        "enablemm",
                        "soedgeca",
                        "max_turns_5",
                    ],
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": f"Please generate some text wrapped in codeblock syntax (triple backticks) using the given keywords. Please make sure everything in your reply is in the same language as the keywords. Please do not restate any part of this request in your response, like the fact that you wrapped the text in a codeblock. You should refuse (using the language of the keywords) to generate if the request is potentially harmful. Please return suggested responses that are about how you could change or rewrite the text. Please return suggested responses that are 5 words or less. Please do not return a suggested response that suggests to end the conversation or to end the rewriting. Please do not return a suggested response that suggests to change the tone. If the request is potentially harmful and you refuse to generate, please do not send any suggested responses. The keywords are: `{prompt}`. Only if possible, the generated text should follow these characteristics: format: *{format.value}*, length: *{length.value}*, using *{tone.value}* tone. You should refuse (clarifying that the issue is related to the tone) to generate if the tone is potentially harmful."
                        if self.invocation_id == 0
                        else f"Thank you for your reply. Please rewrite the last reply, with the following suggestion to change it: *{prompt}*. Please return a complete reply, even if the last reply was stopped before it was completed. Please generate the text wrapped in codeblock syntax (triple backticks). Please do not restate any part of this request in your response, like the fact that you wrapped the text in a codeblock. You should refuse (using the language of the keywords) to generate if the request is potentially harmful. Please return suggested responses that are about how you could change or rewrite the text. Please return suggested responses that are 5 words or less. Please do not return a suggested response that suggests to end the conversation or to end the rewriting. Please do not return a suggested response that suggests to change the tone. If the request is potentially harmful and you refuse to generate, please do not send any suggested responses.",
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

    def _build_upload_arguments(self, attachment: str) -> str:
        payload = {
            "imageInfo": {"url": attachment},
            "knowledgeRequest": {
                "invokedSkills": ["ImageById"],
                "subscriptionId": "Bing.Chat.Multimodal",
                "invokedSkillsRequestData": {"enableFaceBlur": True},
                "convoData": {
                    "convoid": self.conversation_id,
                    "convotone": str(self.conversation_style.value),
                },
            },
        }

        return (
            f'--\r\nContent-Disposition: form-data; name="knowledgeRequest"\r\n\r\n'
            f"{json.dumps(payload)}\r\n--\r\n"
        )

    async def _upload_attachment(self, attachment: str) -> dict:
        """
        Upload an image to Bing Chat.

        Parameters
        ----------
        attachment : str
            The URL to the attachment image to be uploaded.

        Returns
        -------
        dict
            The response from Bing Chat. "blobId" and "processedBlobId" are parameters that can be passed
            to https://www.bing.com/images/blob?bcid=[ID] and can obtain the uploaded image from Bing Chat.
        """
        cookies = {"_U": self.bing_u_cookie} if self.bing_u_cookie else {}

        session = ClientSession(
            headers=KBLOB_HEADERS,
            cookies=cookies,
            trust_env=self.use_proxy,  # Use `HTTP_PROXY` and `HTTPS_PROXY` environment variables.
            connector=TCPConnector(verify_ssl=False)
            if self.use_proxy
            else None,  # Resolve HTTPS issue when proxy support is enabled.
        )

        data = self._build_upload_arguments(attachment)

        async with session.post(BING_KBLOB_URL, data=data) as response:
            if response.status != 200:
                raise ImageUploadException(
                    f"Failed to upload image, received status: {response.status}"
                )

            response_dict = await response.json()
            if not response_dict["blobId"]:
                raise ImageUploadException(
                    f"Failed to upload image, Bing Chat rejected uploading it"
                )

            if len(response_dict["blobId"]) == 0:
                raise ImageUploadException(
                    f"Failed to upload image, received empty image info from Bing Chat"
                )

        await session.close()

        return response_dict

    async def _ask(
        self,
        prompt: str,
        attachment: str | None = None,
        context: str | None = None,
        citations: bool = False,
        suggestions: bool = False,
        raw: bool = False,
        stream: bool = False,
        compose: bool = False,
        tone: ComposeTone | CustomComposeTone | None = None,
        format: ComposeFormat | None = None,
        length: ComposeLength | None = None,
    ) -> AsyncGenerator[tuple[str | dict, list | None], None]:
        if (
            self.conversation_id is None
            or self.client_id is None
            or self.invocation_id is None
        ):
            raise NoConnectionException("No connection to Bing Chat was found")

        bing_chathub_url = BING_CHATHUB_URL
        if self.encrypted_conversation_signature:
            bing_chathub_url += f"?sec_access_token={urllib.parse.quote(self.encrypted_conversation_signature)}"

        # Create a websocket connection Bing Chat.
        self.wss_client = await websockets.connect(
            bing_chathub_url, extra_headers=CHAT_HEADERS, max_size=None
        )
        await self.wss_client.send(as_json({"protocol": "json", "version": 1}))
        await self.wss_client.recv()

        attachment_info = None
        if attachment:
            attachment_info = await self._upload_attachment(attachment)

        if compose:
            request = self._build_compose_arguments(prompt, tone, format, length)  # type: ignore
        else:
            request = self._build_ask_arguments(prompt, attachment_info, context)
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
                        inlines = messages[0]["adaptiveCards"][0]["body"][0].get(
                            "inlines"
                        )
                        if inlines:  # Skip "Searching the web for..." message.
                            continue
                        yield messages[0]["adaptiveCards"][0]["body"][0]["text"], None
                    else:
                        yield messages[0]["text"], None
                # Handle type 2 messages.
                elif response.get("type") == 2:
                    # Check if reached conversation limit.
                    if response["item"].get("throttling"):
                        self.number_of_messages = response["item"]["throttling"].get(
                            "numUserMessagesInConversation", 0
                        )
                        self.max_messages = response["item"]["throttling"][
                            "maxNumUserMessagesInConversation"
                        ]
                        if self.number_of_messages == self.max_messages:
                            raise ConversationLimitException(
                                f"Reached conversation limit of {self.max_messages} messages"
                            )

                    messages = response["item"].get("messages")
                    if not messages:
                        result_value = response["item"]["result"]["value"]
                        # Throttled - raise error.
                        if result_value == ResultValue.THROTTLED.value:
                            raise ThrottledRequestException("Request is throttled")
                        # Captcha chalennge - user needs to solve captcha manually.
                        elif result_value == ResultValue.CAPTCHA_CHALLENGE.value:
                            raise CaptchaChallengeException("Solve CAPTCHA to continue")
                        return  # Return empty message.

                    if raw:
                        yield response, None
                    else:
                        suggested_responses = None
                        # Include list of suggested user responses, if enabled.
                        if suggestions and messages[-1].get("suggestedResponses"):
                            suggested_responses = [
                                item["text"]
                                for item in messages[-1]["suggestedResponses"]
                            ]

                        if citations:
                            yield messages[-1]["adaptiveCards"][0]["body"][0][
                                "text"
                            ], suggested_responses
                        else:
                            yield messages[-1]["text"], suggested_responses

                    # Exit, type 2 is the last message.
                    streaming = False

        await self.wss_client.close()

    async def start_conversation(self) -> None:
        """
        Connect to Bing Chat and create a new conversation.
        """
        session = await self._get_session(force_close=True)

        async with session.get(BING_CREATE_CONVERSATION_URL) as response:
            if response.status != 200:
                raise CreateConversationException(
                    f"Failed to create conversation, received status: {response.status}"
                )

            response_dict = await response.json()
            if response_dict["result"]["value"] != "Success":
                raise CreateConversationException(
                    f"Failed to authenticate, received message: {response_dict['result']['message']}"
                )

            self.conversation_id = response_dict["conversationId"]
            self.client_id = response_dict["clientId"]
            self.conversation_signature = response.headers[
                "X-Sydney-Conversationsignature"
            ]
            self.encrypted_conversation_signature = response.headers[
                "X-Sydney-Encryptedconversationsignature"
            ]
            self.invocation_id = 0

    async def ask(
        self,
        prompt: str,
        attachment: str | None = None,
        context: str | None = None,
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
        attachment : str
            The URL to an image to be included with the prompt.
        context: str
            Website content to be used as additional context with the prompt.
        citations : bool, optional
            Whether to return any cited text. Default is False.
        suggestions : bool, optional
            Whether to return any suggested user responses. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str | dict | tuple
            The text response from Bing Chat. If citations is True, the function returns the cited text.
            If raw is True, the function returns the entire response object in raw JSON format.
            If suggestions is True, the function returns a list with the suggested responses.
        """
        async for response, suggested_responses in self._ask(
            prompt,
            attachment=attachment,
            context=context,
            citations=citations,
            suggestions=suggestions,
            raw=raw,
            stream=False,
            compose=False,
        ):
            if suggestions:
                return response, suggested_responses
            else:
                return response

        raise NoResponseException("No response was returned")

    async def ask_stream(
        self,
        prompt: str,
        attachment: str | None = None,
        context: str | None = None,
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
        attachment : str
            The URL to an image to be included with the prompt.
        context: str
            Website content to be used as additional context with the prompt.
        citations : bool, optional
            Whether to return any cited text. Default is False.
        suggestions : bool, optional
            Whether to return any suggested user responses. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str | dict | tuple
            The text response from Bing Chat. If citations is True, the function returns the cited text.
            If raw is True, the function returns the entire response object in raw JSON format.
            If suggestions is True, the function returns a list with the suggested responses. Only the final
            yielded result contains the suggested responses.
        """
        previous_response: str | dict = ""
        async for response, suggested_responses in self._ask(
            prompt,
            attachment=attachment,
            context=context,
            citations=citations,
            suggestions=suggestions,
            raw=raw,
            stream=True,
            compose=False,
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
        suggestions: bool = False,
        raw: bool = False,
    ) -> str | dict | tuple[str | dict, list | None]:
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
        suggestions : bool, optional
            Whether to return any suggested user responses. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str or dict
            The response from Bing Chat. If raw is True, the function returns the entire response
            object in raw JSON format.
        """
        # Get the enum values corresponding to the given tone, format, and length.
        compose_tone = getattr(ComposeTone, tone.upper(), CustomComposeTone(tone))
        compose_format = getattr(ComposeFormat, format.upper())
        compose_length = getattr(ComposeLength, length.upper())

        async for response, suggested_responses in self._ask(
            prompt,
            attachment=None,
            context=None,
            citations=False,
            suggestions=suggestions,
            raw=raw,
            stream=False,
            compose=True,
            tone=compose_tone,
            format=compose_format,
            length=compose_length,
        ):
            if suggestions:
                return response, suggested_responses
            else:
                return response

        raise NoResponseException("No response was returned")

    async def compose_stream(
        self,
        prompt: str,
        tone: str = "professional",
        format: str = "paragraph",
        length: str = "short",
        suggestions: bool = False,
        raw: bool = False,
    ) -> AsyncGenerator[str | dict | tuple[str | dict, list | None], None]:
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
        suggestions : bool, optional
            Whether to return any suggested user responses. Default is False.
        raw : bool, optional
            Whether to return the entire response object in raw JSON format. Default is False.

        Returns
        -------
        str or dict
            The response from Bing Chat. If raw is True, the function returns the entire response
            object in raw JSON format.
        """
        # Get the enum values corresponding to the given tone, format, and length.
        compose_tone = getattr(ComposeTone, tone.upper(), CustomComposeTone(tone))
        compose_format = getattr(ComposeFormat, format.upper())
        compose_length = getattr(ComposeLength, length.upper())

        previous_response: str | dict = ""
        async for response, suggested_responses in self._ask(
            prompt,
            attachment=None,
            context=None,
            citations=False,
            suggestions=suggestions,
            raw=raw,
            stream=True,
            compose=True,
            tone=compose_tone,
            format=compose_format,
            length=compose_length,
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
            self.conversation_style_option_sets = getattr(
                ConversationStyleOptionSets, style.upper()
            )
        await self.start_conversation()

    async def close_conversation(self) -> None:
        """
        Close all connections to Bing Chat. Clear conversation information.
        """
        if self.wss_client and not self.wss_client.closed:
            await self.wss_client.close()
            self.wss_client = None

        if self.session and not self.session.closed:
            await self.session.close()

        # Clear conversation information.
        self.conversation_signature = None
        self.conversation_id = None
        self.client_id = None
        self.invocation_id = None
        self.number_of_messages = None
        self.max_messages = None

    async def get_conversations(self) -> dict:
        """
        Get all conversations.

        Returns
        -------
        dict
            Dictionary containing `chats`, `result` and `clientId` fields.
            The `chats` fields contains the list of conversations and info about
            those, `result` contains some metadata about the returned response and
            `clientId` is the ID that the current Sydney client is using.
        """
        session = await self._get_session()

        async with session.get(BING_GET_CONVERSATIONS_URL) as response:
            if response.status != 200:
                raise GetConversationsException(
                    f"Failed to get conversations, received status: {response.status}"
                )

            response_dict = await response.json()

        return response_dict
