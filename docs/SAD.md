# AI Media Factory

# System Architecture Document (SAD) v1.0

---

# 1. Purpose

This document defines:

* System components
* Service interactions
* Data flow
* Job lifecycle
* Provider interactions
* Deployment architecture
* Future scaling strategy

The objective is to provide a single architectural reference for development.

---

# 2. Architectural Principles

1. Modular design
2. Configuration-driven behavior
3. Provider abstraction
4. Independent services
5. Failure isolation
6. Human review before publication
7. Future scalability

---

# 3. High-Level Architecture

+----------------------+
| Dashboard (React)    |
+----------------------+
|
v
+----------------------+
| FastAPI Backend      |
+----------------------+
|
v
+----------------------+
| Orchestrator         |
+----------------------+
|
v
+----------------------------------+
| Services Layer                   |
+----------------------------------+
| Topic Service                    |
| Script Service                   |
| Voice Service                    |
| Video Service                    |
| Caption Service                  |
| Renderer Service                 |
| Quality Service                  |
| Upload Service                   |
| Analytics Service                |
+----------------------------------+
|
v
+----------------------------------+
| Provider Layer                   |
+----------------------------------+
| OpenAI                           |
| Gemma                            |
| Edge TTS                         |
| Pexels                           |
| Pixabay                          |
| YouTube API                      |
+----------------------------------+
|
v
+----------------------+
| Database + Storage   |
+----------------------+

---

# 4. Job Flow

CREATE JOB

↓

TOPIC

↓

SCRIPT

↓

VOICE

↓

VISUALS

↓

CAPTIONS

↓

RENDER

↓

QUALITY CHECK

↓

REVIEW

↓

UPLOAD

↓

ANALYTICS

---

# 5. Orchestrator Responsibilities

The Orchestrator is the central controller.

Responsibilities:

* Execute workflow
* Maintain state
* Retry failures
* Trigger services
* Update database
* Send notifications

The orchestrator never performs business logic.

---

# 6. Service Interaction

Example:

Script Service

↓

Calls Script Provider

↓

Receives Script

↓

Stores Result

↓

Returns Success

Services communicate through interfaces.

Services never directly communicate with providers belonging to other services.

---

# 7. Provider Architecture

Every provider implements a common interface.

Example:

ScriptProvider

* generate()

VoiceProvider

* generate()

VideoProvider

* generate()

UploadProvider

* upload()

Providers can be replaced without changing services.

---

# 8. Database Architecture

Tables:

channels

videos

jobs

uploads

analytics

errors

providers

configurations

Relationships:

Channel

↓

Videos

↓

Jobs

↓

Analytics

---

# 9. Storage Architecture

storage/

audio/

captions/

clips/

renders/

cache/

logs/

exports/

Temporary files may be deleted after upload.

Cache files may persist.

---

# 10. Dashboard Architecture

Modules:

Dashboard

Jobs

Queue

Review

Analytics

Settings

Providers

Configuration

The frontend communicates only with FastAPI.

The frontend never accesses providers directly.

---

# 11. Sequence Diagram

User creates job.

↓

API receives request.

↓

Orchestrator creates job.

↓

Script Service executes.

↓

Voice Service executes.

↓

Video Service executes.

↓

Renderer executes.

↓

Quality check executes.

↓

Review queue receives output.

↓

User approves.

↓

Upload executes.

↓

Analytics begins.

---

# 12. Failure Flow

Provider failure.

↓

Retry.

↓

Fallback provider.

↓

Manual review.

↓

Mark failed.

No failure should terminate the application.

---

# 13. Review Flow

Video generated.

↓

Quality checks pass.

↓

Review queue.

↓

Approve.

Reject.

Regenerate.

Edit metadata.

↓

Upload.

---

# 14. Analytics Flow

Upload.

↓

Retrieve metrics.

↓

Store metrics.

↓

Update topic scores.

↓

Generate insights.

Future:

Feedback loop into Topic Service.

---

# 15. Configuration Flow

System startup.

↓

Load YAML.

↓

Validate.

↓

Initialize providers.

↓

Initialize services.

↓

Start orchestrator.

Configuration changes require restart.

Future:

Live configuration reload.

---

# 16. Deployment Architecture (V1)

Single Machine

+------------------+
| React Frontend   |
+------------------+

+------------------+
| FastAPI Backend  |
+------------------+

+------------------+
| SQLite Database  |
+------------------+

+------------------+
| Local Storage    |
+------------------+

All services execute on one machine.

---

# 17. Future Deployment (V2)

Frontend Server

↓

Backend Server

↓

Database Server

↓

Worker Machines

Rendering can be separated.

Uploads can be separated.

---

# 18. Future Deployment (V3)

Cloud Architecture:

Load Balancer

↓

API Servers

↓

Queue Workers

↓

Database Cluster

↓

Storage Service

---

# 19. Monitoring Architecture

Metrics:

* Jobs created
* Jobs failed
* Render time
* Upload success
* API usage
* System health

Logs:

logs/

errors/

performance/

---

# 20. Security Architecture

API keys:

.env

Authentication:

Future version.

Access control:

Future version.

Sensitive data:

Never stored in repositories.

---

# 21. Scalability Strategy

V1:
Single channel.

V2:
Multiple channels.

V3:
Multiple accounts.

V4:
Distributed workers.

V5:
Cloud infrastructure.

---

# 22. Design Rules

Rule 1:
Services never depend on providers.

Rule 2:
Providers never depend on services.

Rule 3:
Configuration drives behavior.

Rule 4:
Failures must be isolated.

Rule 5:
Every component must be replaceable.

Rule 6:
The orchestrator owns workflow.

Rule 7:
The database is the source of truth.

---

# 23. Success Criteria

A successful architecture:

* Supports multiple channels.
* Allows provider replacement.
* Handles failures.
* Supports future scaling.
* Requires no major redesign.
