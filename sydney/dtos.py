from dataclasses import dataclass

@dataclass
class SydneyResponse:
    response: str | None = None
    raw_response: str | None = None
    suggestions: list[str] | None = None
    citations: str | None = None
