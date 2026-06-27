# AI Media Factory

# Database Design Document (DDD) v1.0

---

# 1. Purpose

This document defines:

* Database schema
* Entity relationships
* Table structures
* Status enums
* Constraints
* Future scalability

Database Type:

* SQLite (V1)
* PostgreSQL (Future)

ORM:

* SQLAlchemy

---

# 2. Entity Relationship Overview

Channel

↓

Video

↓

Job

↓

Upload

↓

Analytics

Additional entities:

* Providers
* Errors
* Configurations

---

# 3. Channels Table

Stores YouTube channels managed by the system.

| Field           | Type     | Description        |
| --------------- | -------- | ------------------ |
| id              | UUID     | Primary key        |
| name            | String   | Channel name       |
| niche           | String   | Content niche      |
| youtube_account | String   | Account identifier |
| is_active       | Boolean  | Active status      |
| created_at      | Datetime | Creation date      |
| updated_at      | Datetime | Last update        |

Example:

```text
Dev Shorts
Programming
```

---

# 4. Videos Table

Represents a content idea.

| Field       | Type     |
| ----------- | -------- |
| id          | UUID     |
| channel_id  | UUID     |
| topic       | Text     |
| title       | Text     |
| description | Text     |
| hashtags    | JSON     |
| script      | Text     |
| status      | String   |
| created_at  | Datetime |
| updated_at  | Datetime |

Status:

* CREATED
* PROCESSING
* REVIEW
* APPROVED
* REJECTED
* UPLOADED
* FAILED

---

# 5. Jobs Table

Tracks generation jobs.

| Field         | Type     |
| ------------- | -------- |
| id            | UUID     |
| video_id      | UUID     |
| current_stage | String   |
| progress      | Integer  |
| retry_count   | Integer  |
| status        | String   |
| started_at    | Datetime |
| completed_at  | Datetime |

Stages:

* TOPIC
* SCRIPT
* VOICE
* VIDEO
* CAPTIONS
* RENDER
* QUALITY
* REVIEW
* UPLOAD

---

# 6. Uploads Table

Stores upload information.

| Field            | Type     |
| ---------------- | -------- |
| id               | UUID     |
| video_id         | UUID     |
| youtube_video_id | String   |
| upload_status    | String   |
| upload_time      | Datetime |
| scheduled_time   | Datetime |
| published_time   | Datetime |

Upload status:

* PENDING
* SCHEDULED
* PUBLISHED
* FAILED

---

# 7. Analytics Table

Stores video performance.

| Field        | Type     |
| ------------ | -------- |
| id           | UUID     |
| video_id     | UUID     |
| views        | Integer  |
| likes        | Integer  |
| comments     | Integer  |
| shares       | Integer  |
| watch_time   | Float    |
| retention    | Float    |
| ctr          | Float    |
| collected_at | Datetime |

---

# 8. Errors Table

Stores failures.

| Field         | Type     |
| ------------- | -------- |
| id            | UUID     |
| job_id        | UUID     |
| service       | String   |
| provider      | String   |
| error_message | Text     |
| stack_trace   | Text     |
| retry_count   | Integer  |
| created_at    | Datetime |

---

# 9. Providers Table

Tracks enabled providers.

| Field         | Type     |
| ------------- | -------- |
| id            | UUID     |
| name          | String   |
| type          | String   |
| enabled       | Boolean  |
| configuration | JSON     |
| created_at    | Datetime |

Types:

* SCRIPT
* VOICE
* VIDEO
* CAPTION
* UPLOAD

---

# 10. Configurations Table

Stores runtime configuration.

| Field        | Type     |
| ------------ | -------- |
| id           | UUID     |
| channel_id   | UUID     |
| config_key   | String   |
| config_value | JSON     |
| updated_at   | Datetime |

Examples:

script_provider

voice_provider

quality_rules

upload_rules

---

# 11. Assets Table

Tracks generated assets.

| Field      | Type     |
| ---------- | -------- |
| id         | UUID     |
| video_id   | UUID     |
| asset_type | String   |
| file_path  | String   |
| file_size  | Integer  |
| created_at | Datetime |

Asset types:

* SCRIPT
* AUDIO
* VIDEO
* CAPTION
* THUMBNAIL
* FINAL_RENDER

---

# 12. Review Queue Table

Stores manual review information.

| Field          | Type     |
| -------------- | -------- |
| id             | UUID     |
| video_id       | UUID     |
| review_status  | String   |
| reviewer_notes | Text     |
| reviewed_at    | Datetime |

Statuses:

* PENDING
* APPROVED
* REJECTED
* REGENERATE

---

# 13. Topic Performance Table

Used by future recommendation system.

| Field             | Type    |
| ----------------- | ------- |
| id                | UUID    |
| topic             | String  |
| niche             | String  |
| total_videos      | Integer |
| average_views     | Integer |
| average_retention | Float   |
| performance_score | Float   |

---

# 14. Quota Usage Table

Tracks API usage.

| Field       | Type     |
| ----------- | -------- |
| id          | UUID     |
| provider    | String   |
| quota_limit | Integer  |
| quota_used  | Integer  |
| reset_date  | Datetime |

Examples:

OpenAI

Pexels

YouTube

---

# 15. Notifications Table

Future feature.

| Field      | Type     |
| ---------- | -------- |
| id         | UUID     |
| type       | String   |
| message    | Text     |
| read       | Boolean  |
| created_at | Datetime |

---

# 16. Relationships

Channel

1 → Many Videos

Video

1 → 1 Job

Video

1 → Many Assets

Video

1 → 1 Upload

Video

1 → Many Analytics Records

Job

1 → Many Errors

Video

1 → 1 Review Record

---

# 17. Indexes

Indexes should exist on:

videos.status

videos.channel_id

jobs.status

uploads.youtube_video_id

analytics.video_id

errors.job_id

---

# 18. Soft Delete Strategy

Future:

deleted_at

Instead of physical deletion.

---

# 19. Audit Fields

All tables should include:

created_at

updated_at

Future:

created_by

updated_by

---

# 20. Naming Standards

Tables:

snake_case

Columns:

snake_case

Primary Keys:

id

Foreign Keys:

table_id

Examples:

channel_id

video_id

job_id

---

# 21. V1 Required Tables

channels

videos

jobs

assets

uploads

errors

review_queue

analytics

---

# 22. Future Tables

users

teams

notifications

api_tokens

trend_analysis

competitor_analysis

---

# 23. Database Rules

Rule 1:
Database is the source of truth.

Rule 2:
Services update database state.

Rule 3:
Jobs never exist without videos.

Rule 4:
Errors must always be recorded.

Rule 5:
Every video has a status.

Rule 6:
Every asset belongs to a video.

Rule 7:
Analytics are append-only.
