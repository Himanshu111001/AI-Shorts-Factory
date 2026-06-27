# AI Media Factory

# MVP Scope Document (MSD) v1.0

---

# 1. Purpose

This document defines the Minimum Viable Product (MVP) for AI Media Factory.

The MVP should:

* Produce working YouTube Shorts.
* Require minimal manual work.
* Validate the architecture.
* Validate content quality.
* Validate the workflow.

The MVP should NOT attempt to solve every future problem.

---

# 2. MVP Goal

A user provides a topic.

↓

The system generates:

* Script
* Voice
* Visual assets
* Captions
* Final video

↓

User reviews.

↓

User uploads manually.

---

# 3. Success Criteria

The MVP is successful if:

* One topic can become one Short.
* Generation succeeds consistently.
* Video quality is acceptable.
* User can review output.
* User can export the final MP4.

---

# 4. Target User

Single creator.

Single machine.

Single YouTube channel.

Single operator.

---

# 5. Included Features

## Content Input

* Topic input.

Example:

"React Hooks"

---

## Script Generation

Generate:

* Title
* Script
* Description
* Hashtags

---

## Voice Generation

Generate:

* MP3 narration.

---

## Asset Collection

Obtain:

* Stock footage.
* Images.

---

## Caption Generation

Generate:

* SRT subtitles.

---

## Rendering

Create:

* Vertical MP4.

Aspect ratio:

9:16

---

## Quality Checks

Validate:

* Audio.
* Duration.
* Captions.

---

## Review Queue

User can:

* Approve.
* Reject.

---

## Local Storage

Store:

* Audio.
* Captions.
* Videos.

---

# 6. Excluded Features

The following are NOT part of the MVP.

---

## Automatic Upload

Manual upload only.

---

## Analytics

No YouTube metrics.

---

## Feedback Learning

No topic optimization.

---

## Multi-channel Support

Single channel only.

---

## Multiple Accounts

Single account only.

---

## Trend Analysis

Not included.

---

## Competitor Analysis

Not included.

---

## Quota Management

Not included.

---

## Scheduling

Not included.

---

## Notifications

Not included.

---

## Cloud Deployment

Local machine only.

---

## User Authentication

Not included.

---

# 7. Technology Stack

Backend:

* Python
* FastAPI

Frontend:

* React
* Vite

Database:

* SQLite

Voice:

* Edge TTS

Video:

* Pexels

Captions:

* Faster Whisper

Rendering:

* FFmpeg

---

# 8. User Workflow

Step 1:

Enter topic.

↓

Step 2:

Generate script.

↓

Step 3:

Generate voice.

↓

Step 4:

Generate visuals.

↓

Step 5:

Generate captions.

↓

Step 6:

Render.

↓

Step 7:

Review.

↓

Step 8:

Export.

---

# 9. UI Screens

Dashboard

Create Video

Review Queue

Video Details

Settings

---

# 10. Database Tables Required

channels

videos

jobs

assets

review_queue

errors

---

# 11. API Endpoints Required

POST /videos

POST /jobs

GET /jobs

GET /videos

POST /review/approve

POST /review/reject

---

# 12. Providers Required

Script Provider:

* Local provider

Voice Provider:

* Edge TTS

Video Provider:

* Pexels

Caption Provider:

* Whisper

Renderer:

* FFmpeg

---

# 13. Storage Required

audio/

captions/

clips/

renders/

cache/

---

# 14. Quality Requirements

Video duration:

15–60 seconds.

Audio required.

Captions required.

Vertical format required.

---

# 15. Performance Targets

Script generation:

< 30 seconds.

Voice generation:

< 20 seconds.

Rendering:

< 5 minutes.

Total generation:

< 10 minutes.

---

# 16. MVP Deliverables

Deliverable 1:

Working backend.

Deliverable 2:

Working providers.

Deliverable 3:

Working renderer.

Deliverable 4:

Simple dashboard.

Deliverable 5:

Review system.

---

# 17. Future Phases

V1.1

* Upload API.

V1.2

* Analytics.

V1.3

* Multiple channels.

V2

* AI feedback loops.

V3

* Full automation.

---

# 18. Definition of Done

The MVP is complete when:

1. Topic is entered.

2. Script is generated.

3. Audio is generated.

4. Visual assets are obtained.

5. Captions are generated.

6. Video renders successfully.

7. User approves.

8. Final MP4 exists.

No additional features are required.

---

# 19. Anti-Scope-Creep Rules

Rule 1:

No analytics before rendering works.

Rule 2:

No automation before review works.

Rule 3:

No multiple channels before one channel works.

Rule 4:

No cloud before local works.

Rule 5:

No AI feedback before uploads exist.

---

# 20. MVP Objective

The objective is NOT:

"Build an AI media company."

The objective IS:

"Create one high-quality Short from one topic."

Once this works reliably, future versions can expand safely.
