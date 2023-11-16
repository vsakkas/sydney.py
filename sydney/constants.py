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
