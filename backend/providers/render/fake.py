from backend.providers.render.base import RenderProvider
import os
from pathlib import Path

class FakeRenderProvider(RenderProvider):
    """
    A deterministic fake render provider.
    Used for local development and testing.
    """

    def render_video(
        self,
        audio_path: str,
        image_paths: list[str],
        output_path: str,
    ) -> str:
        if not audio_path or not audio_path.strip():
            raise ValueError("Audio path is required")
            
        if not image_paths:
            raise ValueError("At least one image path is required")
            
        for img in image_paths:
            if not img or not img.strip():
                raise ValueError("Image paths must contain non-empty strings")
                
        if not output_path or not output_path.strip():
            raise ValueError("Output path is required")
            
        out_path = Path(output_path)
        
        # Create output parent directory if necessary
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write deterministic artifact content
        lines = [
            "FAKE_RENDER_ARTIFACT",
            f"AUDIO_PATH:{audio_path.strip()}",
            f"IMAGE_COUNT:{len(image_paths)}"
        ]
        
        for i, img in enumerate(image_paths, 1):
            lines.append(f"IMAGE_{i:03d}:{img.strip()}")
            
        content = "\n".join(lines)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return str(out_path)
