from tempfile import NamedTemporaryFile

import pytest
from aiohttp import ClientSession
from thefuzz import fuzz

from sydney import SydneyClient

URL = "https://github.com/vsakkas/sydney.py/blob/master/images/dog.jpg?raw=true"


@pytest.mark.asyncio
async def test_ask_precise() -> bool:
    expected_responses = [
        "Hello! How can I assist you today?",
        "Hello! How can I assist you today? 😊",
    ]

    async with SydneyClient(style="precise") as sydney:
        response = await sydney.ask("Hello, Copilot!")

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 75:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_balanced() -> bool:
    expected_responses = [
        "Hello! How can I assist you today? 😊",
        "Hello! How can I help you today? 😊",
    ]

    async with SydneyClient(style="balanced") as sydney:
        response = await sydney.ask("Hello, Copilot!")

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 75:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_creative() -> bool:
    expected_responses = [
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you and help you with various tasks. 😊 What would you like to talk about today?",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you and help you with various tasks. 😊 What would you like to talk about?",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you. 😊 What would you like to talk about?",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you. 😊 What would you like to talk about? You can ask me questions, request creative content, or just have a casual conversation. I'm here to help and entertain you. 🙌",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you. 😊 What would you like to talk about? You can ask me questions, request creative content, or just have a casual conversation. I'm here to help. 🙌",
        "Hi there, this is Copilot. I'm an AI companion that can chat with you and help you with various tasks. 😊 What would you like to talk about today?",
    ]

    async with SydneyClient(style="creative") as sydney:
        response = await sydney.ask("Hello, Copilot!")

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 65:  # Lower score since creative mode is unpredictable.
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_precise() -> bool:
    expected_responses = [
        "Hello! How can I assist you today?",
        "Hello! How can I assist you today? 😊",
    ]

    async with SydneyClient(style="precise") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Copilot!"):
            response += response_token  # type: ignore

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 75:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_balanced() -> bool:
    expected_responses = [
        "Hello! How can I assist you today? 😊",
        "Hello! How can I help you today? 😊",
    ]

    async with SydneyClient(style="balanced") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Copilot!"):
            response += response_token  # type: ignore

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 75:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_creative() -> bool:
    expected_responses = [
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you and help you with various tasks. 😊 What would you like to talk about today?",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you and help you with various tasks. 😊 What would you like to talk about?",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you. 😊 What would you like to talk about?",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you. 😊 What would you like to talk about? You can ask me questions, request creative content, or just have a casual conversation. I'm here to help and entertain you. 🙌",
        "Hi there, this is Copilot, your AI companion. I'm happy to chat with you. 😊 What would you like to talk about? You can ask me questions, request creative content, or just have a casual conversation. I'm here to help. 🙌",
        "Hi there, this is Copilot. I'm an AI companion that can chat with you and help you with various tasks. 😊 What would you like to talk about today?",
    ]

    async with SydneyClient(style="creative") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Copilot!"):
            response += response_token  # type: ignore

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 65:  # Lower score since creative mode is unpredictable.
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_suggestions() -> None:
    async with SydneyClient() as sydney:
        _, _ = await sydney.ask("When was Bing Chat released?", suggestions=True)


@pytest.mark.asyncio
async def test_ask_citations() -> None:
    async with SydneyClient() as sydney:
        _ = await sydney.ask("When was Bing Chat released?", citations=True)


@pytest.mark.asyncio
async def test_ask_suggestions_citations() -> None:
    async with SydneyClient() as sydney:
        _, _ = await sydney.ask(
            "When was Bing Chat released?", suggestions=True, citations=True
        )


@pytest.mark.asyncio
async def test_ask_stream_suggestions() -> None:
    async with SydneyClient() as sydney:
        async for _, _ in sydney.ask_stream(
            "When was Bing Chat released?", suggestions=True
        ):
            pass


@pytest.mark.asyncio
async def test_ask_stream_citations() -> None:
    async with SydneyClient() as sydney:
        async for _ in sydney.ask_stream(
            "When was Bing Chat released?", citations=True
        ):
            pass


@pytest.mark.asyncio
async def test_ask_stream_suggestions_citations() -> None:
    async with SydneyClient() as sydney:
        async for _, _ in sydney.ask_stream(
            "When was Bing Chat released?", suggestions=True, citations=True
        ):
            pass


@pytest.mark.asyncio
async def test_ask_raw_suggestions() -> None:
    async with SydneyClient() as sydney:
        _, _ = await sydney.ask(
            "When was Bing Chat released?", suggestions=True, raw=True
        )


@pytest.mark.asyncio
async def test_ask_raw_citations() -> None:
    async with SydneyClient() as sydney:
        _ = await sydney.ask("When was Bing Chat released?", citations=True, raw=True)


@pytest.mark.asyncio
async def test_ask_raw_suggestions_citations() -> None:
    async with SydneyClient() as sydney:
        _, _ = await sydney.ask(
            "When was Bing Chat released?", suggestions=True, citations=True, raw=True
        )


@pytest.mark.asyncio
async def test_ask_attachment_url() -> None:
    async with SydneyClient() as sydney:
        response = await sydney.ask("What does this image show?", attachment=URL)

        assert isinstance(response, str)
        assert "puppy" in response.lower()


@pytest.mark.asyncio
async def test_ask_attachment_file() -> None:
    with NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        file_path = temp_file.name

        async with ClientSession() as session:
            async with session.get(URL) as response:
                temp_file.write(await response.read())

        async with SydneyClient() as sydney:
            response = await sydney.ask(
                "What does this image show?", attachment=file_path
            )

            assert isinstance(response, str)
            assert "puppy" in response.lower()


@pytest.mark.asyncio
async def test_ask_multiple_prompts() -> None:
    async with SydneyClient() as sydney:
        _ = await sydney.ask("Tell me a joke.")

        _ = await sydney.ask("Tell me another one.")


@pytest.mark.asyncio
async def test_ask_logic_precise() -> bool:
    expected_responses = [
        "You have **4 apples** today. The apples you ate yesterday do not affect the number of apples you have today. So, you still have **4 apples**. Enjoy your apples! 🍎",
        "You have **4 apples** today. The apples you ate yesterday don't affect the number of apples you have today. So, you still have **4 apples**. Enjoy your apples! 🍎",
        "You mentioned that you have 4 apples today. The apples you ate yesterday do not affect the number of apples you have today. So, you still have **4 apples** today. Enjoy your apples! 🍎",
        "You still have **4 apples** today. The apples you ate yesterday don't affect the number of apples you have today. Enjoy your apples! 🍎",
    ]

    async with SydneyClient(style="precise") as sydney:
        response = await sydney.ask(
            "I have 4 apples today. I ate 3 apples yesterday. How many apples do I have today?",
            search=False,
        )

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"
