from abc import ABC, abstractmethod

class AudioGenerationProvider(ABC):
    """
    Abstract base class defining the contract for AI audio generation.
    Any concrete AI audio provider must implement this interface.
    """

    @abstractmethod
    def generate_audio(self, text: str, output_path: str) -> str:
        """
        Convert narration text into an audio file.
        
        Args:
            text: The narration/script input.
            output_path: The requested destination path for the audio file.
            
        Returns:
            The final audio file path as a string.
        """
        raise NotImplementedError
