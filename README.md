 # Azure Speech REST Python SDK (lightweight)
 
 A minimal, httpx-based wrapper for Azure Speech REST APIs (speech-to-text, text-to-speech, and translation). The goal is to mirror the public SDK surface where possible while remaining compatible with environments where the official SDK wheels are unavailable.
 
 ## Installation
 
 ```bash
 pip install -e .[dev]
 ```
 
 ## Quick start
 
 ```python
 from azure_speech import SpeechClient, SpeechConfig
 
 config = SpeechConfig.from_subscription("YOUR_KEY", region="eastus")
 client = SpeechClient(config)
 
 # Text-to-speech
 result = client.speak_text("Hello from Azure Speech!")
 with open("hello.mp3", "wb") as f:
     f.write(result.audio)
 
 # Speech-to-text
 with open("sample.wav", "rb") as f:
     audio_bytes = f.read()
stt = client.recognize(audio_bytes)
print(stt.text)
```

### Async usage

```python
import asyncio
from azure_speech import SpeechClient, SpeechConfig

async def main():
    async with SpeechClient(SpeechConfig.from_authorization_token("YOUR_TOKEN", region="eastus")) as client:
        result = await client.speak_text_async("Hello from Azure Speech async!")
        with open("hello_async.mp3", "wb") as f:
            f.write(result.audio)

asyncio.run(main())
```

## Authentication
 
 You can authenticate with either an Azure Cognitive Services subscription key or an Azure Active Directory bearer token.
 
 ```python
 SpeechConfig.from_authorization_token("<token>", region="eastus")
 ```
 
 ## Examples
 
 See [`examples/synthesize.py`](examples/synthesize.py) for a runnable sample using environment variables.
 
 ## Notes
 
 - Uses only `httpx` for HTTP communication.
 - Surfaces simple result objects (`SpeechSynthesisResult`, `SpeechRecognitionResult`) mirroring the official SDK names.
 - Provides basic input validation and error handling via `AzureSpeechError`.
