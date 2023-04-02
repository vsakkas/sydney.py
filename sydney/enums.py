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


class ComposeTone(Enum):
    """
    Bing Chat compose tones. Supported options are:
    - `professional` for formal conversations in a professional setting
    - `casual` for informal conversations between friends or family members
    - `enthusiastic` for conversations where the writer wants to convey excitement or passion
    - `informational` for conversations where the writer wants to convey information or knowledge
    - `funny` for conversations where the writer wants to be humorous or entertaining
    """

    professional = "professional"
    casual = "casual"
    enthusiastic = "enthusiastic"
    informational = "informational"
    funny = "funny"


class ComposeFormat(Enum):
    """
    Bing Chat compose formats. Supported options are:
    - `paragraph` for longer messages that are composed of multiple sentences or paragraphs
    - `email` for messages that are structured like emails, with a clear subject line and formal greeting and closing
    - `blogpost` for messages that are structured like blog posts, with clear headings and subheadings and a more informal tone
    - `ideas` for messages that are used to brainstorm or share ideas
    """

    paragraph = "paragraph"
    email = "email"
    blogpost = "blog post"
    ideas = "ideas"


class ComposeLength(Enum):
    """
    Bing Chat compose lengths. Supported options are:
    - `short` for messages that are only a few words or sentences long
    - `medium` for messages that are a few paragraphs long
    - `long` for messages that are several paragraphs or pages long
    """

    short = "short"
    medium = "medium"
    long = "long"
