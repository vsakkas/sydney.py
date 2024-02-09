import pytest

from sydney import SydneyClient


@pytest.mark.asyncio
async def test_get_conversations() -> None:
    async with SydneyClient() as sydney:
        _ = await sydney.ask("Hello, Bing!")

        response = await sydney.get_conversations()

        assert "chats" in response
        assert "result" in response
        assert "clientId" in response


@pytest.mark.asyncio
async def test_get_conversations_no_start_conversation() -> None:
    sydney = SydneyClient()

    response = await sydney.get_conversations()

    await sydney.close_conversation()

    assert "chats" in response
    assert "result" in response
    assert "clientId" in response
