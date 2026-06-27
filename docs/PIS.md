# AI Media Factory

# Provider Interface Specification (PIS) v1.0

---

# 1. Purpose

This document defines:

* Provider contracts
* Standard interfaces
* Request formats
* Response formats
* Error handling
* Provider lifecycle

Every provider must follow these rules.

---

# 2. Provider Principles

Rule 1:
Providers are replaceable.

Rule 2:
Services communicate only with interfaces.

Rule 3:
Providers never call other providers.

Rule 4:
Providers never access the database.

Rule 5:
Providers never contain business logic.

Rule 6:
Providers only perform one task.

---

# 3. Base Provider Interface

All providers implement:

```python
class BaseProvider:

    def initialize(self):
        pass

    def validate(self):
        pass

    def execute(self):
        pass

    def health(self):
        pass
```

---

# 4. Standard Response Format

Success:

```python
{
    "success": True,
    "data": {},
    "metadata": {}
}
```

Failure:

```python
{
    "success": False,
    "error": {
        "code": "ERROR_CODE",
        "message": "Description"
    }
}
```

---

# 5. Script Provider

Purpose:

Generate scripts.

Interface:

```python
generate(topic: str)
```

Input:

```python
"React Hooks"
```

Output:

```python
{
    "title": "...",
    "script": "...",
    "description": "...",
    "hashtags": []
}
```

Providers:

* OpenAIProvider
* GemmaProvider
* LocalProvider

---

# 6. Voice Provider

Purpose:

Convert text to speech.

Interface:

```python
generate(script)
```

Output:

```python
{
    "audio_path": "audio.mp3",
    "duration": 42
}
```

Providers:

* EdgeTTSProvider
* PiperProvider

---

# 7. Video Provider

Purpose:

Provide visual assets.

Interface:

```python
generate(script)
```

Output:

```python
{
    "clips": [
        "clip1.mp4",
        "clip2.mp4"
    ]
}
```

Providers:

* PexelsProvider
* PixabayProvider
* VeoProvider

---

# 8. Caption Provider

Purpose:

Generate subtitles.

Interface:

```python
generate(audio_path)
```

Output:

```python
{
    "caption_path": "captions.srt"
}
```

Providers:

* WhisperProvider

---

# 9. Renderer Provider

Purpose:

Create final video.

Interface:

```python
render(inputs)
```

Output:

```python
{
    "video_path": "output.mp4"
}
```

Providers:

* FFmpegRenderer
* MoviePyRenderer

---

# 10. Upload Provider

Purpose:

Upload content.

Interface:

```python
upload(video_path)
```

Output:

```python
{
    "video_id": "youtube_id",
    "url": "youtube_url"
}
```

Providers:

* YouTubeProvider

---

# 11. Analytics Provider

Purpose:

Retrieve performance.

Interface:

```python
fetch(video_id)
```

Output:

```python
{
    "views": 1000,
    "retention": 75
}
```

---

# 12. Health Checks

Every provider implements:

```python
health()
```

Example:

```python
{
    "healthy": True
}
```

---

# 13. Validation

Every provider implements:

```python
validate()
```

Checks:

* API keys
* Dependencies
* Disk space
* Configuration

---

# 14. Retry Rules

Temporary failures:

* Retry.

Permanent failures:

* Return error.

Retries:

* Attempt 1
* Attempt 2
* Attempt 3

Then fail.

---

# 15. Logging

Providers log:

* Start.
* Success.
* Failure.
* Duration.

Providers never write directly to files.

Logging service handles logs.

---

# 16. Configuration Access

Providers receive:

```python
provider_config
```

Example:

```python
{
    "voice": "en-US"
}
```

Providers never load YAML directly.

---

# 17. Dependency Rules

Allowed:

Provider

↓

External API

Forbidden:

Provider

↓

Database

Provider

↓

Other providers

Provider

↓

Frontend

---

# 18. Provider Lifecycle

Initialize

↓

Validate

↓

Execute

↓

Return result

↓

Shutdown

---

# 19. Example Script Provider

```python
class OpenAIProvider(ScriptProvider):

    def generate(self, topic):
        pass
```

---

# 20. Example Voice Provider

```python
class EdgeTTSProvider(VoiceProvider):

    def generate(self, script):
        pass
```

---

# 21. Future Providers

Script:

* Claude
* Gemini
* Local LLM

Voice:

* ElevenLabs
* OpenVoice

Video:

* Runway
* Veo
* Kling

Upload:

* Instagram
* TikTok

---

# 22. Naming Standards

Examples:

OpenAIProvider

EdgeTTSProvider

PexelsProvider

WhisperProvider

---

# 23. File Structure

providers/

script/

voice/

video/

caption/

upload/

analytics/

---

# 24. Error Codes

PROVIDER_NOT_FOUND

INVALID_CONFIG

API_ERROR

QUOTA_EXCEEDED

TIMEOUT

DEPENDENCY_FAILURE

UNKNOWN_ERROR

---

# 25. Provider Rules

Rule 1:
Single responsibility.

Rule 2:
Stateless.

Rule 3:
Replaceable.

Rule 4:
No business logic.

Rule 5:
No database access.

Rule 6:
Standard responses.

Rule 7:
Graceful failures.
