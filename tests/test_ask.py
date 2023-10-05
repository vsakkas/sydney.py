import pytest

from sydney import SydneyClient
from thefuzz import fuzz


@pytest.mark.asyncio
async def test_ask_precise() -> bool:
    expected_responses = [
        "Hello! This is Bing. How can I help you today? 😊",
        "Hello! How can I help you today? 😊",
        "Hello! How can I assist you today?"
    ]

    async with SydneyClient(style="precise") as sydney:
        response = await sydney.ask("Hello, Bing!")

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_balanced() -> bool:
    expected_responses = ["Hello! How can I help you today? 😊"]

    async with SydneyClient(style="balanced") as sydney:
        response = await sydney.ask("Hello, Bing!")

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_creative() -> bool:
    expected_responses = [
        "Hello, this is Bing. How can I help? 😊",
        "Hello, this is Bing. Nice to meet you! 😊",
        "Hi, this is Bing. I'm happy to chat with you. 😊 What would you like to talk about?",
        "Hi, this is Bing. I'm a chat mode of Microsoft Bing that can help you with various tasks and queries. I can also generate creative content such as poems, stories, code, essays, songs, celebrity parodies, and more. What would you like to talk about? 🤗"
    ]

    async with SydneyClient(style="creative") as sydney:
        response = await sydney.ask("Hello, Bing!")

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_precise() -> bool:
    expected_responses = [
        "Hello! This is Bing. How can I help you today? 😊",
        "Hello! How can I help you today? 😊",
        "Hello! How can I assist you today?"
    ]

    async with SydneyClient(style="precise") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Bing!"):
            response += response_token

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_balanced() -> bool:
    expected_responses = ["Hello! How can I help you today? 😊"]

    async with SydneyClient(style="balanced") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Bing!"):
            response += response_token

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_creative() -> bool:
    expected_responses = [
        "Hello, this is Bing. How can I help? 😊",
        "Hello, this is Bing. Nice to meet you! 😊",
        "Hi, this is Bing. I'm happy to chat with you. 😊 What would you like to talk about?",
        "Hi, this is Bing. I'm a chat mode of Microsoft Bing that can help you with various tasks and queries. I can also generate creative content such as poems, stories, code, essays, songs, celebrity parodies, and more. What would you like to talk about? 🤗"
    ]

    async with SydneyClient(style="creative") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Bing!"):
            response += response_token

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"
