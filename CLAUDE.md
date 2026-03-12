# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Install dependencies (use public PyPI — internal registries may block packages)
.venv/bin/pip install -r requirements.txt -i https://pypi.org/simple/

# Start dev server (auto-reloads on file changes)
.venv/bin/uvicorn app.main:app --reload --port 8000
```

If port 8000 is already in use, find and kill the conflicting process:
```bash
lsof -i :8000 | grep LISTEN
kill <PID>
```

## Architecture

The app is a FastAPI server with Jinja2-rendered HTML pages and a REST API. There is no database — articles are stored as Markdown files with YAML frontmatter in `content/`.

**Storage layer** (`app/storage.py`): All file I/O lives here. Functions return plain `dict` objects (not ORM models). Templates and routes access fields via dot notation (Jinja2 supports dict dot access). Timestamps are stored as ISO strings in frontmatter and parsed back to `datetime` objects by `_to_datetime()` on read.

**Two routers:**
- `app/routes/articles.py` — REST API at `/api/articles/*`, uses Pydantic models for request/response validation
- `app/routes/pages.py` — HTML page routes at `/`, `/articles/{slug}`, `/new`, `/edit/{slug}`, `/tags/{tag}`

**Article file format:**
```markdown
---
title: Article Title
summary: One-line description
tags: tag1, tag2, tag3
created_at: "2026-03-12T03:49:00+00:00"
updated_at: "2026-03-12T03:49:00+00:00"
---

Markdown content here...
```

## Key Behaviours

- **Slug = filename**: `content/{slug}.md`. Renaming an article (title change) renames the file.
- **Tags** are comma-separated strings stored in frontmatter. Tag filtering is done in-memory in `pages.py` and `storage.py` — no indexing.
- **Markdown preview** (`POST /api/articles/_preview`) renders content server-side and returns HTML — used by the editor's Preview tab.
- The `content/` directory is git-tracked. Articles edited via the web UI are committed as regular file changes.
