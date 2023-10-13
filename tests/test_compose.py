import pytest

from sydney import SydneyClient


@pytest.mark.asyncio
async def test_compose() -> None:
    async with SydneyClient() as sydney:
        _ = await sydney.compose(
            prompt="Why Python is a great language", format="ideas"
        )


@pytest.mark.asyncio
async def test_compose_stream() -> None:
    async with SydneyClient() as sydney:
        async for _ in sydney.compose_stream(
            prompt="Why Python is a great language", format="ideas"
        ):
            pass


@pytest.mark.asyncio
async def test_compose_custom_tone() -> None:
    async with SydneyClient() as sydney:
        _ = await sydney.compose(
            prompt="Why Python is a great language",
            format="ideas",
            tone="concise",
        )


@pytest.mark.asyncio
async def test_compose_suggestions() -> None:
    async with SydneyClient() as sydney:
        _, _ = await sydney.compose(
            prompt="Why Python is a great language", format="ideas", suggestions=True
        )
