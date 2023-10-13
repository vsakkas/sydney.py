CHAT_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47",
}
KBLOB_HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "multipart/form-data",
    "Referer": "https://www.bing.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
}

BING_CREATE_CONVERSATION_URL = "https://edgeservices.bing.com/edgesvc/turing/conversation/create"
BING_GET_CONVERSATIONS_URL = "https://www.bing.com/turing/conversation/chats"
BING_CHATHUB_URL = "wss://sydney.bing.com/sydney/ChatHub"
BING_KBLOB_URL = "https://www.bing.com/images/kblob"
BING_BLOB_URL = "https://www.bing.com/images/blob?bcid="

DELIMETER = "\x1e"  # Record separator character.
