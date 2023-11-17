USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/117.0.2045.60"

CHAT_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://www.bing.com",
    "Referer": "https://www.bing.com/",
    "Sec-Ch-Ua": '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="118"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": USER_AGENT,
}

CREATE_HEADERS = {
    "Authority": "www.bing.com",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.bing.com/copilot",
    "Sec-Ch-Ua": '"Microsoft Edge";v="117", "Chromium";v="118", "Not?A_Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Ms-Gec": "0D3C55EA3A4602964E5474BD9C1D472632FD8E3280D266A5C761A0C6CD4C7595",
    "Sec-Ms-Gec-Version": "1-119.0.2151.58",
    "User-Agent": USER_AGENT,
    "X-Edge-Shopping-Flag": "0",
}

CHATHUB_HEADERS = {
    "Pragma": "no-cache",
    "Origin": "https://www.bing.com",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": USER_AGENT,
    "Upgrade": "websocket",
    "Cache-Control": "no-cache",
    "Connection": "Upgrade",
    "Sec-WebSocket-Version": "13",
    "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
}


KBLOB_HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "multipart/form-data",
    "Referer": "https://www.bing.com/",
    "User-Agent": USER_AGENT,
}

BUNDLE_VERSION = "1.1342.3-cplt.7"

BING_CREATE_CONVERSATION_URL = (
    f"https://www.bing.com/turing/conversation/create?bundleVersion={BUNDLE_VERSION}"
)
BING_GET_CONVERSATIONS_URL = "https://www.bing.com/turing/conversation/chats"
BING_CHATHUB_URL = "wss://sydney.bing.com/sydney/ChatHub"
BING_KBLOB_URL = "https://www.bing.com/images/kblob"
BING_BLOB_URL = "https://www.bing.com/images/blob?bcid="

DELIMETER = "\x1e"  # Record separator character.
