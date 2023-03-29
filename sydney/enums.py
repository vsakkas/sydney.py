from enum import Enum


class ConversationStyle(Enum):
    """
    Bing Chat conversation styles. Supported options are:
    - `creative` for original and imaginative chat
    - `balanced` for informative and friendly chat
    - `precise` for concise and straightforward chat
    """

    creative = "h3relaxedimg"
    balanced = "galileo"
    precise = "h3precise"
