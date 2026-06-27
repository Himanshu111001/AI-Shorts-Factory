# AI Media Factory

# API Specification Document (ASD) v1.0

---

# 1. Purpose

This document defines:

* REST API endpoints
* Request formats
* Response formats
* Status codes
* Error handling
* Future API expansion

API Style:

* RESTful API

Framework:

* FastAPI

Response Format:

* JSON

---

# 2. Base URL

Development:

/api/v1

Examples:

/api/v1/jobs

/api/v1/videos

---

# 3. Standard Response Format

Success:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

Error:

```json
{
  "success": false,
  "error": "Error message"
}
```

---

# 4. Health Endpoint

GET /health

Purpose:

Check application health.

Response:

```json
{
  "status": "healthy"
}
```

---

# 5. Channels API

## Create Channel

POST /channels

Request:

```json
{
  "name": "Dev Shorts",
  "niche": "Programming"
}
```

Response:

```json
{
  "id": "uuid"
}
```

---

## Get Channels

GET /channels

Response:

```json
[
  {
    "id": "uuid",
    "name": "Dev Shorts"
  }
]
```

---

## Get Channel

GET /channels/{id}

---

## Update Channel

PUT /channels/{id}

---

## Delete Channel

DELETE /channels/{id}

---

# 6. Video API

## Create Video

POST /videos

Request:

```json
{
  "channel_id": "uuid",
  "topic": "React Hooks"
}
```

Response:

```json
{
  "video_id": "uuid"
}
```

---

## Get Videos

GET /videos

Query Parameters:

status

channel_id

page

limit

---

## Get Video

GET /videos/{id}

---

## Delete Video

DELETE /videos/{id}

---

# 7. Job API

## Create Job

POST /jobs

Request:

```json
{
  "video_id": "uuid"
}
```

---

## Get Jobs

GET /jobs

---

## Get Job

GET /jobs/{id}

Response:

```json
{
  "status": "PROCESSING",
  "progress": 70,
  "current_stage": "VOICE"
}
```

---

## Retry Job

POST /jobs/{id}/retry

---

## Cancel Job

POST /jobs/{id}/cancel

---

# 8. Script API

## Generate Script

POST /scripts/generate

Request:

```json
{
  "topic": "React Hooks"
}
```

Response:

```json
{
  "title": "...",
  "script": "...",
  "hashtags": []
}
```

---

# 9. Voice API

## Generate Voice

POST /voice/generate

Request:

```json
{
  "video_id": "uuid"
}
```

---

# 10. Video Asset API

## Generate Assets

POST /assets/generate

Request:

```json
{
  "video_id": "uuid"
}
```

---

# 11. Caption API

## Generate Captions

POST /captions/generate

Request:

```json
{
  "video_id": "uuid"
}
```

---

# 12. Renderer API

## Render Video

POST /render

Request:

```json
{
  "video_id": "uuid"
}
```

Response:

```json
{
  "status": "success",
  "file": "output.mp4"
}
```

---

# 13. Quality API

## Run Quality Check

POST /quality/check

Response:

```json
{
  "passed": true,
  "checks": {
    "audio": true,
    "captions": true,
    "duration": true
  }
}
```

---

# 14. Review API

## Get Review Queue

GET /review

---

## Approve Video

POST /review/{id}/approve

---

## Reject Video

POST /review/{id}/reject

Request:

```json
{
  "reason": "Audio issue"
}
```

---

## Regenerate Video

POST /review/{id}/regenerate

---

# 15. Upload API

## Upload Video

POST /upload

Request:

```json
{
  "video_id": "uuid"
}
```

---

## Schedule Upload

POST /upload/schedule

Request:

```json
{
  "video_id": "uuid",
  "publish_at": "datetime"
}
```

---

# 16. Analytics API

## Get Analytics

GET /analytics

---

## Video Analytics

GET /analytics/{video_id}

Response:

```json
{
  "views": 5000,
  "retention": 72,
  "ctr": 6.5
}
```

---

# 17. Error API

## Get Errors

GET /errors

---

## Get Error

GET /errors/{id}

---

# 18. Provider API

## Get Providers

GET /providers

---

## Enable Provider

POST /providers/{id}/enable

---

## Disable Provider

POST /providers/{id}/disable

---

# 19. Configuration API

## Get Config

GET /config

---

## Update Config

PUT /config

---

# 20. Dashboard API

GET /dashboard

Response:

```json
{
  "videos_today": 4,
  "uploads_today": 2,
  "failed_jobs": 1,
  "pending_reviews": 3
}
```

---

# 21. Status Codes

200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

500 Internal Server Error

---

# 22. Error Response

```json
{
  "success": false,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "Video does not exist"
  }
}
```

---

# 23. Pagination

Request:

?page=1&limit=20

Response:

```json
{
  "page": 1,
  "limit": 20,
  "total": 100,
  "items": []
}
```

---

# 24. Future APIs

Authentication

User Management

Notifications

Teams

Competitor Analysis

Trend Analysis

AI Recommendations

---

# 25. API Rules

Rule 1:
All responses use JSON.

Rule 2:
Errors use standard format.

Rule 3:
API never exposes internal provider logic.

Rule 4:
Frontend only talks to API.

Rule 5:
Services never talk directly to frontend.

Rule 6:
Database access only through services.
