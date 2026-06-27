# AI Media Factory

# Technical Requirements Document (TRD) v1.0

---

# 1. Purpose

This document defines the technical architecture, components, communication patterns, data flow, technology choices, and implementation standards for AI Media Factory.

The objective is to ensure:

* Maintainability
* Scalability
* Replaceable providers
* Low operational cost
* AI-assisted development compatibility

---

# 2. Architecture Style

The system follows a:

## Modular Service Architecture

Each component operates independently and communicates through service interfaces.

Principles:

* Loose coupling
* High cohesion
* Provider abstraction
* Configuration-driven behavior

---

# 3. System Architecture

User Interface

↓

API Layer

↓

Orchestrator

↓

Services

↓

Providers

↓

Storage

---

# 4. Core Components

## 4.1 Orchestrator

Responsibilities:

* Execute job pipeline
* Track job status
* Manage retries
* Call services
* Handle failures

Input:

* Job request

Output:

* Completed job

---

## 4.2 Topic Service

Responsibilities:

* Topic generation
* Topic validation
* Topic scheduling

Future:

* Trending analysis
* Competitor analysis

---

## 4.3 Script Service

Responsibilities:

* Generate scripts
* Create titles
* Generate descriptions
* Generate hashtags

Interface:

generate(topic)

---

## 4.4 Voice Service

Responsibilities:

* Convert text to audio
* Select voice
* Manage TTS providers

Interface:

generate(script)

---

## 4.5 Video Service

Responsibilities:

* Fetch visual assets
* Download clips
* Select images

Interface:

generate(script)

---

## 4.6 Caption Service

Responsibilities:

* Generate subtitles
* Sync timestamps
* Export SRT

---

## 4.7 Renderer Service

Responsibilities:

* Combine assets
* Render video
* Export MP4

---

## 4.8 Quality Service

Responsibilities:

* Verify duration
* Check audio
* Check subtitles
* Validate output

---

## 4.9 Upload Service

Responsibilities:

* Upload video
* Schedule upload
* Update status

---

## 4.10 Analytics Service

Responsibilities:

* Track views
* Track retention
* Track CTR

---

# 5. Provider Architecture

Every service uses providers.

Example:

ScriptService

↓

ScriptProvider

↓

OpenAIProvider

GemmaProvider

LocalProvider

---

Provider rules:

* Providers are interchangeable.
* Services never depend on implementation.
* Providers return standardized responses.

---

# 6. Provider Response Format

Success:

{
"success": true,
"data": {}
}

Failure:

{
"success": false,
"error": "message"
}

---

# 7. Job Lifecycle

CREATED

↓

PROCESSING

↓

RENDERING

↓

REVIEW

↓

APPROVED

↓

UPLOADED

↓

ANALYZED

Possible failure:

FAILED

---

# 8. Technology Stack

## Backend

* Python 3.12
* FastAPI

## ORM

* SQLAlchemy

## Validation

* Pydantic

## Database

* SQLite (V1)
* PostgreSQL (future)

## Queue

* In-memory queue (V1)
* Celery (future)

## Video

* FFmpeg
* MoviePy

## Voice

* Edge TTS

## Captions

* Faster Whisper

## Frontend

* React
* Vite
* Tailwind

---

# 9. Folder Structure

backend/

api/

services/

providers/

models/

schemas/

orchestrator/

utils/

config/

frontend/

components/

pages/

hooks/

storage/

audio/

videos/

captions/

renders/

cache/

configs/

docs/

---

# 10. Configuration System

Configuration files use YAML.

Example:

channel:
name: dev_shorts

providers:
script: local
voice: edge
video: pexels

quality:
min_duration: 15
max_duration: 60

---

# 11. API Design

POST /jobs

Create content job.

GET /jobs

List jobs.

GET /jobs/{id}

Job details.

POST /jobs/{id}/approve

Approve job.

POST /jobs/{id}/reject

Reject job.

POST /jobs/{id}/upload

Upload video.

GET /analytics

Performance metrics.

---

# 12. Database Tables

channels

videos

jobs

uploads

analytics

errors

providers

---

# 13. Error Handling

Errors shall:

* Never crash the application.
* Be logged.
* Be retried.

Retry policy:

Attempt 1

↓

Attempt 2

↓

Attempt 3

↓

FAILED

---

# 14. Logging

Log levels:

DEBUG

INFO

WARNING

ERROR

CRITICAL

Logs stored in:

logs/

---

# 15. Quality Rules

Minimum duration: 15 seconds.

Maximum duration: 60 seconds.

Audio required.

Subtitles required.

Vertical aspect ratio required.

No empty frames.

---

# 16. Review Queue

States:

PENDING

APPROVED

REJECTED

REGENERATE

---

# 17. Security

API keys stored in:

.env

Never commit:

* API keys
* Tokens
* Credentials

---

# 18. Scalability Strategy

V1:
Single machine.

V2:
Multiple channels.

V3:
Distributed workers.

V4:
Cloud deployment.

---

# 19. Performance Targets

Video generation:

< 10 minutes.

API response:

< 500 ms.

Dashboard loading:

< 2 seconds.

Failure rate:

< 10%.

---

# 20. Future Technical Enhancements

* Celery workers
* Redis queues
* Docker deployment
* Kubernetes
* Cloud rendering
* AI optimization agents
* Multi-user support
