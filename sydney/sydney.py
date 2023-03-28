import json
import os

import websockets.client as websockets
from aiohttp import ClientSession

HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
}

BING_CREATE_CONVESATION_URL = "https://www.bing.com/turing/conversation/create"
BING_CHATHUB_URL = "wss://sydney.bing.com/sydney/ChatHub"

RECORD_SEPARATOR = "\x1e"


def as_json(message: dict) -> str:
    """
    Convert message to JSON, append record separator character at the end.
    """
    return json.dumps(message) + RECORD_SEPARATOR


class SydneyClient:
    def __init__(self) -> None:
        self.conversation_id = None
        self.client_id = None
        self.conversation_signature = None
        self.invocation_id = None
        self.wss_client = None

    async def start_conversation(self) -> None:
        """
        Connect to Bing Chat API and create a new conversation.
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

        await session.close()

    async def ask(self, prompt: str) -> str:
        """
        Send a prompt to Bing Chat API using the current conversation.
        """
        if self.wss_client:
            if not self.wss_client.closed:
                await self.wss_client.close()
        
        # Create a connection to Bing Chat API.
        self.wss_client = await websockets.connect(
            BING_CHATHUB_URL, extra_headers=HEADERS, max_size=None
        )
        await self.wss_client.send(as_json({"protocol": "json", "version": 1}))
        await self.wss_client.recv()
        await self.wss_client.send(as_json({"type": 6}))
        await self.wss_client.recv()

        request = {
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
        self.invocation_id += 1

        await self.wss_client.send(as_json(request))
        while True:
            objects = str(await self.wss_client.recv()).split(RECORD_SEPARATOR)
            for obj in objects:
                if not obj:
                    continue
                response = json.loads(obj)
                if response.get("type") == 2:
                    return response

    async def reset_conversation(self) -> None:
        """
        Clear current conversation information and connection and start new ones.
        """
        await self.close()
        await self.start_conversation()

    async def close(self) -> None:
        """
        Close all connections to Bing Chat API. Clear conversation information.
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
