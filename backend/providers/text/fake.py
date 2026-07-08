from backend.providers.text.base import TextGenerationProvider

class FakeTextGenerationProvider(TextGenerationProvider):
    """
    A deterministic fake AI text generation provider.
    Used for local development and testing without incurring API costs
    or dealing with non-deterministic external dependencies.
    """

    def generate_title(self, topic: str, niche: str) -> str:
        return f"{topic} | {niche}"

    def generate_description(self, topic: str, title: str, niche: str) -> str:
        return f"A short video about {topic}. Created for the {niche} niche."

    def generate_script(self, topic: str, title: str, niche: str) -> str:
        return f"Today we're talking about {topic}. This content is for viewers interested in {niche}."

    def generate_hashtags(self, topic: str, title: str, niche: str) -> list[str]:
        def normalize_hashtag(text: str) -> str:
            # Simple normalizer: lowercase, replace spaces with underscores, add # prefix
            clean_text = text.strip().lower().replace(" ", "_")
            # In case the string was empty after strip
            if not clean_text:
                return "#default"
            return f"#{clean_text}"
            
        return [
            normalize_hashtag(topic),
            normalize_hashtag(niche),
            "#fake_generated"
        ]
