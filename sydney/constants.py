USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/131.0.2903.86"

CREATE_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://edgeservices.bing.com/edgesvc/chat",
    "Sec-Ch-Ua": '"Microsoft Edge";v="131", "Chromium";v="132", "Not?A_Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": USER_AGENT,
    "X-Edge-Shopping-Flag": "0",
}

CHATHUB_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "Upgrade",
    "Origin": "https://copilot.microsoft.com",
    "Pragma": "no-cache",
    "User-Agent": USER_AGENT,
}

KBLOB_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "multipart/form-data",
    "Referer": "https://copilot.microsoft.com/",
    "Sec-Ch-Ua": '"Microsoft Edge";v="131", "Chromium";v="132", "Not?A_Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": USER_AGENT,
    "X-Edge-Shopping-Flag": "0",
}

BUNDLE_VERSION = "1.1816.0"

BING_CREATE_CONVERSATION_URL = f"https://edgeservices.bing.com/turing/conversation/create?bundleVersion={BUNDLE_VERSION}"
BING_GET_CONVERSATIONS_URL = "https://edgeservices.bing.com/turing/conversation/chats"
BING_CHATHUB_URL = "wss://sydney.bing.com/sydney/ChatHub"
BING_KBLOB_URL = "https://edgeservices.bing.com/images/kblob"
BING_BLOB_URL = "https://edgeservices.bing.com/images/blob?bcid="

DELIMETER = "\x1e"  # Record separator character.
