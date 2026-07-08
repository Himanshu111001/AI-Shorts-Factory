import logging
from google import genai
from google.genai.errors import APIError

from backend.providers.text.base import TextGenerationProvider
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

class GeminiTextGenerationProvider(TextGenerationProvider):
    """
    Real AI text generation provider using Google's Gemini models.
    Leverages the official google-genai SDK.
    """

    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured in application settings.")
        
        try:
            self.client = genai.Client(api_key=settings.gemini_api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")
            
        # Hardcoding the model for now, can be moved to settings later
        self.model_name = "gemini-2.5-flash"

    def _generate(self, prompt: str) -> str:
        """
        Internal helper to execute the API call and handle errors uniformly.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            if not response.text:
                raise ValueError("Gemini API returned an empty response.")
            return response.text.strip()
        except APIError as e:
            logger.error(f"Gemini API Error: {e}")
            raise ValueError(f"Gemini API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Gemini generation: {e}")
            raise ValueError(f"Unexpected error during Gemini generation: {e}")

    def generate_title(self, topic: str, niche: str) -> str:
        prompt = (
            f"Generate a short, catchy YouTube Shorts title about '{topic}' "
            f"for the '{niche}' niche. Respond with ONLY the title, no quotes or extra text."
        )
        return self._generate(prompt)

    def generate_description(self, topic: str, title: str, niche: str) -> str:
        prompt = (
            f"Generate a 2-3 sentence YouTube Shorts description for a video titled '{title}' "
            f"about '{topic}' in the '{niche}' niche. Keep it engaging."
        )
        return self._generate(prompt)

    def generate_script(self, topic: str, title: str, niche: str) -> str:
        prompt = (
            f"Write a 60-second YouTube Shorts script for a video titled '{title}' "
            f"about '{topic}'. Target audience: '{niche}'. "
            f"Do not include camera directions or scene descriptions, just the raw spoken text."
        )
        return self._generate(prompt)

    def generate_hashtags(self, topic: str, title: str, niche: str) -> list[str]:
        prompt = (
            f"Generate exactly 5 relevant hashtags for a YouTube Shorts video titled '{title}' "
            f"about '{topic}' in the '{niche}' niche. "
            f"Return them as a comma-separated list without any extra text."
        )
        response_text = self._generate(prompt)
        
        # Clean and format the comma-separated hashtags
        raw_hashtags = [h.strip() for h in response_text.split(',')]
        formatted_hashtags = []
        
        for tag in raw_hashtags:
            if not tag:
                continue
            if not tag.startswith('#'):
                formatted_hashtags.append(f"#{tag}")
            else:
                formatted_hashtags.append(tag)
                
        if not formatted_hashtags:
            raise ValueError("Failed to parse valid hashtags from Gemini response.")
            
        return formatted_hashtags
