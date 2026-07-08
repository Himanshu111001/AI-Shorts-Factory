import os
from backend.providers.audio.base import AudioGenerationProvider

class FakeAudioGenerationProvider(AudioGenerationProvider):
    """
    A deterministic fake AI audio generation provider.
    Used for local development and testing without incurring API costs.
    """

    def generate_audio(self, text: str, output_path: str) -> str:
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty or whitespace-only")
            
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create deterministic fake audio artifact
        # We use the length and the stripped text to ensure determinism
        artifact_content = f"FAKE_AUDIO_ARTIFACT\nTEXT_LENGTH:{len(text)}\nTEXT:{text.strip()}"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(artifact_content)
            
        return output_path
