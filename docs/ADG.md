# AI Media Factory

# Antigravity Development Guide (ADG) v1.0

---

# 1. Purpose

This document defines how AI-assisted development should be performed using Antigravity.

Goals:

* Consistent architecture.
* Small implementation tasks.
* Reduced hallucinations.
* High-quality code.
* Minimal rewrites.

---

# 2. Development Philosophy

The developer is responsible for:

* Architecture.
* Requirements.
* Code review.
* Testing.
* Integration.

Antigravity is responsible for:

* Implementation.
* Boilerplate.
* Refactoring.
* Unit tests.
* Documentation.

Never delegate architecture decisions to AI.

---

# 3. Golden Rule

Bad:

"Build the AI Media Factory."

Good:

"Implement Sprint 3 Task 2 according to PIS v1.0."

---

# 4. Context Documents

Before requesting implementation, provide:

* PRD
* TRD
* PIS
* FRS
* Relevant sprint section

AI should never receive the entire documentation set unless necessary.

---

# 5. Task Size

Ideal:

1 file.

Maximum:

3–5 related files.

Avoid:

* Entire services.
* Entire applications.
* Multiple features.

---

# 6. Prompt Structure

Always provide:

1. Objective.
2. Inputs.
3. Outputs.
4. Constraints.
5. Existing architecture.
6. Files to create.

---

Example:

Objective:
Implement EdgeTTSProvider.

Requirements:
Follow PIS v1.0.

Files:
providers/voice/edge_provider.py

Return:
Code only.

---

# 7. Allowed Tasks

Good tasks:

* Create database model.
* Create API route.
* Create provider.
* Create service.
* Write tests.
* Refactor function.

---

# 8. Forbidden Tasks

Avoid:

* Build entire backend.
* Create complete dashboard.
* Build all providers.
* Design architecture.
* Decide folder structure.

---

# 9. Development Order

1. Models.
2. Repositories.
3. Services.
4. Providers.
5. APIs.
6. UI.

Never reverse this order.

---

# 10. One Responsibility Rule

One prompt.

One objective.

Bad:

"Build script service and voice service."

Good:

"Build ScriptService."

---

# 11. Code Generation Rules

AI must:

* Follow FRS.
* Follow PIS.
* Follow naming rules.
* Use type hints.
* Include docstrings.

---

# 12. File Creation Rules

AI should only create:

* Requested files.
* Necessary dependencies.

AI should not:

* Rename files.
* Move files.
* Delete files.

---

# 13. Review Checklist

Before accepting code:

* Does it follow the architecture?
* Does it violate dependencies?
* Does it belong in the correct folder?
* Does it include typing?
* Does it include error handling?

---

# 14. Dependency Rules

Allowed:

API

↓

Service

↓

Repository

↓

Database

Forbidden:

Provider

↓

Database

API

↓

Provider

UI

↓

Database

---

# 15. Refactoring Rules

Refactor only when:

* File exceeds 500 lines.
* Multiple responsibilities exist.
* Code duplication occurs.

Do not refactor working code unnecessarily.

---

# 16. Testing Prompts

Example:

"Write pytest tests for EdgeTTSProvider."

Never ask:

"Test the entire system."

---

# 17. Debugging Prompts

Provide:

* Error.
* Stack trace.
* Relevant files.
* Expected behavior.

Avoid:

"It doesn't work."

---

# 18. Integration Rules

After every feature:

1. Run tests.
2. Start backend.
3. Verify APIs.
4. Check logs.

Only then continue.

---

# 19. Commit Rules

One feature.

One commit.

Examples:

feat: add script provider

feat: add edge tts provider

fix: handle upload failures

---

# 20. Context Size Rules

Small tasks:

1 document.

Medium tasks:

2–3 documents.

Large tasks:

Maximum 5 documents.

Too much context reduces output quality.

---

# 21. Preferred Prompt Template

Task:
Implement EdgeTTSProvider.

Documents:
PIS v1.0
FRS v1.0

Requirements:

* Follow VoiceProvider interface.
* Return standard response.
* Save output in storage/audio.

Deliverables:

* edge_provider.py
* unit tests

Constraints:

* No database access.
* No business logic.

---

# 22. Code Review Rules

Accept code only if:

* Compiles.
* Follows architecture.
* Includes typing.
* Includes error handling.
* Includes logging.

---

# 23. Architecture Violations

Immediate rejection:

* Provider accessing database.
* Service calling external API directly.
* API containing business logic.
* Hardcoded configuration.
* Circular imports.

---

# 24. Recovery Strategy

If AI generates poor code:

1. Stop.
2. Reduce task size.
3. Add more context.
4. Regenerate.

Never patch fundamentally incorrect code.

---

# 25. Development Workflow

Read documentation.

↓

Create task.

↓

Prompt Antigravity.

↓

Review code.

↓

Run tests.

↓

Commit.

↓

Continue.

---

# 26. Rule of 80%

If generated code is:

80% correct:

Fix manually.

Less than 80%:

Regenerate.

---

# 27. AI Responsibilities

AI:

* Code.
* Tests.
* Documentation.
* Refactoring.

Human:

* Architecture.
* Decisions.
* Reviews.
* Releases.

---

# 28. Final Rule

AI writes code.

The developer owns the system.
