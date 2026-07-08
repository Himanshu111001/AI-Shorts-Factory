import os
from backend.providers.image.base import ImageGenerationProvider

class FakeImageGenerationProvider(ImageGenerationProvider):
    """
    A deterministic fake AI image generation provider.
    Used for local development and testing without incurring API costs.
    """

    def generate_images(
        self,
        prompts: list[str],
        output_dir: str,
    ) -> list[str]:
        if not prompts:
            raise ValueError("Input prompts list cannot be empty")
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        paths = []
        count = len(prompts)
        
        for i, prompt in enumerate(prompts, 1):
            if not prompt or not prompt.strip():
                raise ValueError("Input prompt cannot be empty or whitespace-only")
                
            stripped_prompt = prompt.strip()
            filename = f"image_{i:03d}.fake"
            output_path = os.path.join(output_dir, filename)
            
            artifact_content = f"FAKE_IMAGE_ARTIFACT\nINDEX:{i}\nTOTAL:{count}\nPROMPT:{stripped_prompt}"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(artifact_content)
                
            paths.append(output_path)
            
        return paths
