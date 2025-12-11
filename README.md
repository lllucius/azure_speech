 # Azure Speech REST Python SDK (lightweight)
 
 A minimal, httpx-based wrapper for Azure Speech REST APIs (speech-to-text, text-to-speech, and translation). This SDK **mimics the official Azure Speech SDK for Python** (`azure-cognitiveservices-speech`) as closely as possible, allowing code to work with both SDKs with minimal changes.
 
 ## Features
 
 - **Official SDK-compatible API**: Use `SpeechSynthesizer`, `SpeechRecognizer`, `SpeechConfig`, `AudioConfig`, and `ResultReason` just like the official SDK
 - **Simplified API**: Also provides a simplified `SpeechClient` for quick usage
 - **REST-based**: Uses Azure Speech REST APIs via httpx (no native dependencies)
 - **Async support**: Full async/await support for both API styles
 - **Lightweight**: Minimal dependencies, works in environments where official SDK wheels are unavailable
 
 ## Installation
 
 ```bash
 pip install -e .[dev]
 ```
 
 ## Quick Start

 ### Official SDK-Compatible API (Recommended)
 
 Use the same API as the official Azure Speech SDK:
 
 ```python
 from azure_speech import SpeechConfig, SpeechSynthesizer, SpeechRecognizer
 
 # Create speech config (mimics official SDK)
 speech_config = SpeechConfig(subscription="YOUR_KEY", region="eastus")
 
 # Text-to-speech
 synthesizer = SpeechSynthesizer(speech_config=speech_config)
 result = synthesizer.speak_text_async("Hello from Azure Speech!")
 with open("hello.mp3", "wb") as f:
     f.write(result.audio)
 print(f"Result reason: {result.reason}")
 
 # Speech-to-text
 recognizer = SpeechRecognizer(speech_config=speech_config)
 with open("sample.wav", "rb") as f:
     audio_bytes = f.read()
 result = recognizer.recognize_once_async(audio_bytes)
 print(f"Recognized: {result.text}")
 print(f"Result reason: {result.reason}")
 ```
 
 ### Simplified API (Alternative)
 
 For simpler use cases, use the `SpeechClient`:
 
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

### Async Usage

Both APIs support async/await:

```python
import asyncio
from azure_speech import SpeechConfig, SpeechSynthesizer

async def main():
    speech_config = SpeechConfig(subscription="YOUR_KEY", region="eastus")
    synthesizer = SpeechSynthesizer(speech_config=speech_config)
    
    # Use the truly async methods
    result = await synthesizer.speak_text_async_real("Hello async!")
    with open("hello_async.mp3", "wb") as f:
        f.write(result.audio)
    
    await synthesizer.aclose()

asyncio.run(main())
```

## Authentication
 
You can authenticate with either an Azure Cognitive Services subscription key or an Azure Active Directory bearer token:
 
```python
# Using subscription key (official SDK style)
speech_config = SpeechConfig(subscription="YOUR_KEY", region="eastus")

# Using authorization token (official SDK style)
speech_config = SpeechConfig(authorization_token="YOUR_TOKEN", region="eastus")

# Using helper methods
config1 = SpeechConfig.from_subscription("YOUR_KEY", region="eastus")
config2 = SpeechConfig.from_authorization_token("YOUR_TOKEN", region="eastus")
```
 
## Examples
 
- [`examples/official_sdk_example.py`](examples/official_sdk_example.py) - Using the official SDK-compatible API
- [`examples/synthesize.py`](examples/synthesize.py) - Using the simplified SpeechClient API
- [`examples/synthesize_async.py`](examples/synthesize_async.py) - Async usage with SpeechClient
 
## API Compatibility

This SDK mimics the official Azure Speech SDK (`azure-cognitiveservices-speech`) API:

| This SDK | Official SDK | Notes |
|----------|-------------|-------|
| `SpeechConfig(subscription=key, region=region)` | `speechsdk.SpeechConfig(subscription=key, region=region)` | ✓ Compatible |
| `SpeechSynthesizer(speech_config=config)` | `speechsdk.SpeechSynthesizer(speech_config=config)` | ✓ Compatible |
| `SpeechRecognizer(speech_config=config)` | `speechsdk.SpeechRecognizer(speech_config=config)` | ✓ Compatible |
| `synthesizer.speak_text_async(text)` | `synthesizer.speak_text_async(text).get()` | Similar (REST API limitation: no .get() needed) |
| `recognizer.recognize_once_async(audio)` | `recognizer.recognize_once_async().get()` | Similar (REST API takes audio bytes directly) |
| `AudioConfig` | `speechsdk.AudioConfig` | Placeholder for API compatibility |
| `ResultReason` | `speechsdk.ResultReason` | ✓ Compatible enum |

## Notes
 
- REST-based implementation using `httpx` for HTTP communication
- No native dependencies - works in environments where official SDK wheels are unavailable
- Result objects (`SpeechSynthesisResult`, `SpeechRecognitionResult`) match official SDK structure
- Includes `reason` property with `ResultReason` enum for compatibility
- `AudioConfig` is a placeholder for API compatibility (REST API doesn't support microphone input)
- Provides both official SDK-compatible API and simplified `SpeechClient` API
