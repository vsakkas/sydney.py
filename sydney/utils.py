import json

from sydney.constants import DELIMETER


def as_json(message: dict) -> str:
    """
    Convert message to JSON, append delimeter character at the end.
    """
    return json.dumps(message) + DELIMETER
