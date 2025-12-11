"""
Example: Using the official Azure Speech SDK-compatible API.

This example demonstrates how to use the SDK with API that mimics
the official Azure Speech SDK for Python (azure-cognitiveservices-speech).

Environment variables:
- AZURE_SPEECH_KEY (optional when AZURE_SPEECH_TOKEN provided)
- AZURE_SPEECH_TOKEN (bearer token)
- AZURE_SPEECH_REGION (e.g., eastus)
"""
import os
from pathlib import Path

# Import using official SDK-style classes
from azure_speech import SpeechConfig, SpeechSynthesizer, SpeechRecognizer


def main() -> None:
    region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
    key = os.environ.get("AZURE_SPEECH_KEY")
    token = os.environ.get("AZURE_SPEECH_TOKEN")
    
    # Create SpeechConfig using official SDK-style constructor
    if token:
        speech_config = SpeechConfig(authorization_token=token, region=region)
    elif key:
        speech_config = SpeechConfig(subscription=key, region=region)
    else:
        raise SystemExit("Set AZURE_SPEECH_KEY or AZURE_SPEECH_TOKEN.")
    
    # Text-to-Speech using SpeechSynthesizer (official SDK style)
    print("=== Text-to-Speech Example ===")
    synthesizer = SpeechSynthesizer(speech_config=speech_config)
    
    # Use speak_text_async (mimics official SDK method name)
    result = synthesizer.speak_text_async("Hello from the Azure Speech SDK compatible API!")
    
    output = Path("output_official.mp3")
    output.write_bytes(result.audio)
    print(f"✓ Wrote synthesized audio to {output}")
    print(f"  Result reason: {result.reason}")
    print(f"  Request ID: {result.request_id}")
    
    # Speech-to-Text using SpeechRecognizer (official SDK style)
    # Note: This is just a demonstration. In a real scenario, you would have actual audio data.
    print("\n=== Speech-to-Text Example (demonstration) ===")
    recognizer = SpeechRecognizer(speech_config=speech_config)
    print("✓ Created SpeechRecognizer")
    print("  To recognize speech, call: result = recognizer.recognize_once_async(audio_bytes)")
    
    # Demonstrate SSML usage
    print("\n=== SSML Example ===")
    ssml = '''<speak version="1.0" xml:lang="en-US">
        <voice name="en-US-JennyNeural">
            <prosody rate="slow" pitch="-2st">
                Hello from SSML!
            </prosody>
        </voice>
    </speak>'''
    
    result_ssml = synthesizer.speak_ssml_async(ssml)
    output_ssml = Path("output_ssml.mp3")
    output_ssml.write_bytes(result_ssml.audio)
    print(f"✓ Wrote SSML synthesized audio to {output_ssml}")
    
    synthesizer.close()
    recognizer.close()
    print("\n✓ Done! SDK usage matches official Azure Speech SDK patterns.")


if __name__ == "__main__":
    main()
