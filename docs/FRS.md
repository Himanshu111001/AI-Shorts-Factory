# AI Media Factory

# Folder Structure & Repository Standard (FRS) v1.0

---

# 1. Purpose

This document defines:

* Repository structure
* Folder responsibilities
* Naming conventions
* File placement rules
* Asset organization

The repository structure must remain stable throughout the project lifecycle.

---

# 2. Repository Structure

```text
ai-media-factory/

├── backend/
├── frontend/
├── storage/
├── configs/
├── docs/
├── scripts/
├── tests/
├── logs/
├── .env
├── .gitignore
├── docker-compose.yml
├── README.md
└── requirements.txt
```

---

# 3. Backend Structure

```text
backend/

├── api/
├── orchestrator/
├── services/
├── providers/
├── models/
├── schemas/
├── repositories/
├── config/
├── utils/
├── middleware/
├── jobs/
├── exceptions/
└── main.py
```

---

# 4. API Folder

```text
api/

├── channels.py
├── videos.py
├── jobs.py
├── uploads.py
├── analytics.py
├── providers.py
└── health.py
```

Responsibilities:

* Route definitions.
* Request handling.
* Response generation.

No business logic.

---

# 5. Orchestrator

```text
orchestrator/

├── job_orchestrator.py
├── pipeline_manager.py
├── retry_manager.py
└── workflow_engine.py
```

Responsibilities:

* Control execution flow.
* Trigger services.
* Manage retries.

---

# 6. Services

```text
services/

├── topic/
├── script/
├── voice/
├── video/
├── captions/
├── render/
├── quality/
├── upload/
└── analytics/
```

Example:

```text
services/script/

├── service.py
├── validator.py
└── formatter.py
```

---

# 7. Providers

```text
providers/

├── script/
├── voice/
├── video/
├── captions/
├── upload/
└── analytics/
```

Example:

```text
providers/script/

├── openai_provider.py
├── gemma_provider.py
└── local_provider.py
```

---

# 8. Models

Database models.

```text
models/

├── channel.py
├── video.py
├── job.py
├── upload.py
├── analytics.py
└── error.py
```

---

# 9. Schemas

Pydantic schemas.

```text
schemas/

├── channel.py
├── video.py
├── job.py
└── analytics.py
```

---

# 10. Repositories

Database access.

```text
repositories/

├── channel_repository.py
├── video_repository.py
└── job_repository.py
```

Only repositories access the database.

---

# 11. Config

```text
config/

├── settings.py
├── environment.py
└── provider_loader.py
```

---

# 12. Middleware

```text
middleware/

├── logging.py
├── error_handler.py
└── request_timer.py
```

---

# 13. Jobs

Background jobs.

```text
jobs/

├── render_job.py
├── upload_job.py
└── analytics_job.py
```

---

# 14. Exceptions

```text
exceptions/

├── provider_exception.py
├── validation_exception.py
└── upload_exception.py
```

---

# 15. Frontend Structure

```text
frontend/

├── public/
├── src/
├── package.json
└── vite.config.js
```

---

# 16. Frontend Source

```text
src/

├── components/
├── pages/
├── services/
├── hooks/
├── stores/
├── layouts/
├── routes/
├── types/
└── utils/
```

---

# 17. Components

Reusable UI.

```text
components/

├── cards/
├── tables/
├── forms/
├── charts/
└── modals/
```

---

# 18. Pages

```text
pages/

├── Dashboard/
├── Jobs/
├── Videos/
├── Review/
├── Analytics/
└── Settings/
```

---

# 19. Frontend Services

API clients.

```text
services/

├── job_api.ts
├── video_api.ts
└── analytics_api.ts
```

---

# 20. Storage

```text
storage/

├── audio/
├── captions/
├── clips/
├── renders/
├── cache/
├── thumbnails/
└── exports/
```

---

# 21. Audio

Generated speech.

Example:

```text
audio/

12345.mp3
```

---

# 22. Clips

Downloaded footage.

```text
clips/

react/
python/
coding/
```

---

# 23. Renders

Final videos.

```text
renders/

video_001.mp4
```

---

# 24. Cache

Reusable assets.

```text
cache/

typing.mp4
keyboard.mp4
coding.mp4
```

---

# 25. Configurations

```text
configs/

channels/
providers/
quality/
```

Example:

```text
configs/channels/

dev_shorts.yaml
```

---

# 26. Documentation

```text
docs/

PRD.md
TRD.md
SAD.md
DDD.md
ASD.md
PIS.md
FRS.md
```

---

# 27. Scripts

Utility scripts.

```text
scripts/

seed_database.py
cleanup.py
backup.py
```

---

# 28. Tests

```text
tests/

unit/
integration/
providers/
services/
```

---

# 29. Logs

```text
logs/

application.log
errors.log
jobs.log
```

---

# 30. Naming Rules

Python:

snake_case

Examples:

video_service.py

job_repository.py

Classes:

PascalCase

Examples:

VideoService

EdgeTTSProvider

Variables:

snake_case

---

# 31. Import Rules

Allowed:

API

↓

Service

↓

Repository

↓

Database

Forbidden:

API

↓

Provider

Provider

↓

Repository

---

# 32. Maximum File Size

Recommended:

300–500 lines.

Maximum:

1000 lines.

Large files should be split.

---

# 33. Feature Rule

Every feature should contain:

* Service
* Schema
* API
* Tests

---

# 34. Provider Rule

Every provider folder contains:

provider.py

config.py

tests.py

---

# 35. Future Expansion

Future folders:

```text
workers/
notifications/
teams/
authentication/
```

---

# 36. Repository Rules

Rule 1:
One responsibility per folder.

Rule 2:
No business logic in APIs.

Rule 3:
No database access outside repositories.

Rule 4:
Providers remain isolated.

Rule 5:
Services contain business logic.

Rule 6:
Storage never contains source code.

Rule 7:
Documentation lives in docs/.
