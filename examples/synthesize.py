 """
 Example: convert text to speech using subscription key or AAD bearer token.
 
 Environment variables:
 - AZURE_SPEECH_KEY (optional when AZURE_SPEECH_TOKEN provided)
 - AZURE_SPEECH_TOKEN (bearer token)
 - AZURE_SPEECH_REGION (e.g., eastus)
 """
 import os
 from pathlib import Path
 
 from azure_speech import SpeechClient, SpeechConfig
 
 
 def main() -> None:
     region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
     key = os.environ.get("AZURE_SPEECH_KEY")
     token = os.environ.get("AZURE_SPEECH_TOKEN")
     if token:
         config = SpeechConfig.from_authorization_token(token, region=region)
     elif key:
         config = SpeechConfig.from_subscription(key, region=region)
     else:
         raise SystemExit("Set AZURE_SPEECH_KEY or AZURE_SPEECH_TOKEN.")
 
     client = SpeechClient(config)
     result = client.speak_text("Hello from the lightweight Azure Speech REST SDK!")
 
     output = Path("output.mp3")
     output.write_bytes(result.audio)
     print(f"Wrote synthesized audio to {output}")
 
 
 if __name__ == "__main__":
     main()
