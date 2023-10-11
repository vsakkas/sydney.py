import pytest

from sydney import SydneyClient


@pytest.mark.asyncio
async def test_compose() -> None:
    expected_responses = [
        "Hello! This is Bing. How can I help you today? 😊",
        "Hello! How can I help you today? 😊",
        "Hello! How can I assist you today?",
    ]

    async with SydneyClient() as sydney:
        _ = await sydney.compose(
            prompt="Why Python is a great language", format="ideas"
        )


@pytest.mark.asyncio
async def test_compose_stream() -> None:
    expected_responses = [
        "Hello! This is Bing. How can I help you today? 😊",
        "Hello! How can I help you today? 😊",
        "Hello! How can I assist you today?",
    ]

    async with SydneyClient() as sydney:
        async for _ in sydney.compose_stream(
            prompt="Why Python is a great language", format="ideas"
        ):
            pass
