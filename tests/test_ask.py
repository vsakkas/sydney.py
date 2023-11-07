import pytest
from thefuzz import fuzz

from sydney import SydneyClient

URL = "https://github.com/vsakkas/sydney.py/blob/master/images/dog.jpg?raw=true"


@pytest.mark.asyncio
async def test_ask_precise() -> bool:
    expected_responses = [
        "Hello! This is Bing. How can I help you today? 😊",
        "Hello! How can I help you today? 😊",
        "Hello! How can I assist you today?",
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
        "Hello! How can I help you today? 😊",
        "Hello, this is Bing. How can I help? 😊",
        "Hello, this is Bing. Nice to meet you! 😊",
        "Hi, this is Bing. I'm happy to chat with you. 😊 What would you like to talk about?",
        "Hi, this is Bing. I'm a chat mode of Microsoft Bing that can help you with various tasks and queries. I can also generate creative content such as poems, stories, code, essays, songs, celebrity parodies, and more. What would you like to talk about? 🤗",
        "Hi, this is Bing. I'm glad you're here. 😊 I can help you with various tasks, such as searching the web, creating graphic art, generating creative content, and more. Just ask me anything and I'll do my best to assist you. 🙌 What would you like to do today,?"
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
        "Hello! How can I assist you today?",
    ]

    async with SydneyClient(style="precise") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Bing!"):
            response += response_token  # type: ignore

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
            response += response_token  # type: ignore

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"


@pytest.mark.asyncio
async def test_ask_stream_creative() -> bool:
    expected_responses = [
        "Hello! How can I help you today? 😊",
        "Hello, this is Bing. How can I help? 😊",
        "Hello, this is Bing. Nice to meet you! 😊",
        "Hi, this is Bing. I'm happy to chat with you. 😊 What would you like to talk about?",
        "Hi, this is Bing. I'm a chat mode of Microsoft Bing that can help you with various tasks and queries. I can also generate creative content such as poems, stories, code, essays, songs, celebrity parodies, and more. What would you like to talk about? 🤗",
    ]

    async with SydneyClient(style="creative") as sydney:
        response = ""
        async for response_token in sydney.ask_stream("Hello, Bing!"):
            response += response_token  # type: ignore

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
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
async def test_ask_attachment() -> None:
    async with SydneyClient() as sydney:
        response = await sydney.ask("What does this image show?", attachment=URL)

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
            "I have 4 apples today. I ate 3 apples yesterday. How many apples do I have today?"
        )

        score = 0
        for expected_response in expected_responses:
            score = fuzz.token_sort_ratio(response, expected_response)
            if score >= 80:
                return True

        assert False, f"Unexpected response: {response}, match score: {score}"
