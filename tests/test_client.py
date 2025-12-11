import asyncio

import httpx
import pytest

from azure_speech import AzureSpeechError, SpeechClient, SpeechConfig


def test_speak_text_uses_subscription_key_and_returns_audio():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Ocp-Apim-Subscription-Key"] == "test-key"
        assert request.headers["X-Microsoft-OutputFormat"] == "audio-16khz-32kbitrate-mono-mp3"
        assert request.url == httpx.URL("https://eastus.tts.speech.microsoft.com/cognitiveservices/v1")
        return httpx.Response(200, content=b"audio-bytes", headers={"X-RequestId": "req-123"})

    transport = httpx.MockTransport(handler)
    client = SpeechClient(SpeechConfig.from_subscription("test-key", region="eastus"), transport=transport)

    result = client.speak_text("hello world")

    assert result.audio == b"audio-bytes"
    assert result.request_id == "req-123"
    assert result.format == "audio-16khz-32kbitrate-mono-mp3"


def test_recognize_with_bearer_token_returns_result():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token-123"
        assert request.url.params.get("language") == "en-US"
        return httpx.Response(
            200,
            json={
                "DisplayText": "hello speech",
                "Duration": 100,
                "Offset": 5,
            },
        )

    transport = httpx.MockTransport(handler)
    client = SpeechClient(
        SpeechConfig.from_authorization_token("token-123", region="eastus"),
        transport=transport,
    )

    result = client.recognize(b"\x00\x01", language="en-US")

    assert result.text == "hello speech"
    assert result.duration == 100
    assert result.offset == 5
    assert result.raw["DisplayText"] == "hello speech"


def test_translate_returns_translations_map():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get_list("to") == ["de-DE", "fr-FR"]
        payload = {
            "text": "hello",
            "translations": [
                {"to": "de-DE", "text": "hallo"},
                {"to": "fr-FR", "text": "bonjour"},
            ],
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    client = SpeechClient(SpeechConfig.from_subscription("abc", region="eastus"), transport=transport)

    result = client.translate(b"audio", to=["de-DE", "fr-FR"])

    assert result.recognized == "hello"
    assert result.translations == {"de-DE": "hallo", "fr-FR": "bonjour"}


def test_error_response_raises_custom_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "bad request"}})

    transport = httpx.MockTransport(handler)
    client = SpeechClient(SpeechConfig.from_subscription("abc", region="eastus"), transport=transport)

    with pytest.raises(AzureSpeechError) as exc:
        client.speak_text("bad")

    assert "bad request" in str(exc.value)


def test_async_speak_text_with_token_and_streaming():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token-xyz"
        assert request.headers["X-Microsoft-OutputFormat"] == "audio-16khz-32kbitrate-mono-mp3"
        return httpx.Response(200, content=b"async-audio")

    transport = httpx.MockTransport(handler)
    client = SpeechClient(
        SpeechConfig.from_authorization_token("token-xyz", region="eastus"),
        async_transport=transport,
    )

    result = asyncio.run(client.speak_text_async("hello async"))
    assert result.audio == b"async-audio"

    chunks = list(asyncio.run(_collect_async_stream(client.stream_synthesis_async("hello async"))))
    assert b"async-audio" in b"".join(chunks)


async def _collect_async_stream(generator):
    collected = []
    async for chunk in generator:
        collected.append(chunk)
    return collected


def test_async_translate_maps_translations_and_respects_targets():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get_list("to") == ["es-ES"]
        payload = {
            "text": "hello",
            "translations": [
                {"to": "es-ES", "text": "hola"},
                None,
            ],
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    client = SpeechClient(SpeechConfig.from_subscription("abc", region="eastus"), async_transport=transport)

    result = asyncio.run(client.translate_async(b"audio", to=["es-ES"]))
    assert result.recognized == "hello"
    assert result.translations == {"es-ES": "hola"}


def test_set_authorization_token_updates_headers():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer new-token"
        return httpx.Response(200, content=b"audio")

    transport = httpx.MockTransport(handler)
    client = SpeechClient(SpeechConfig.from_authorization_token("old", region="eastus"), transport=transport)
    client.set_authorization_token("new-token")
    client.speak_text("hello")
