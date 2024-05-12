import json
from datetime import datetime
from urllib.parse import urlparse

from sydney.constants import DELIMETER


def as_json(message: dict) -> str:
    """
    Convert message to JSON, append delimeter character at the end.
    """
    return json.dumps(message) + DELIMETER


def cookies_as_dict(cookies: str) -> dict:
    """
    Convert a string of cookies into a dictionary.
    """
    return {
        key_value.strip().split("=")[0]: "=".join(key_value.split("=")[1:])
        for key_value in cookies.split(";")
    }


def check_if_url(string: str) -> bool:
    parsed_string = urlparse(string)
    if parsed_string.scheme and parsed_string.netloc:
        return True
    return False


def get_iso_timestamp() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()
