---
created_at: 2026-03-12 12:02:42.566824+00:00
summary: A real example of using Claude Code to scaffold, code, and deploy a full-stack
  web app from scratch in one conversation.
tags: Claude, AI Coding, FastAPI, Python, Case Study
title: Building an AI Knowledge Hub with Claude Code
updated_at: 2026-03-12 12:12:52.361610+00:00
---

# Building an AI Knowledge Hub with Claude Code

This article documents a real conversation where Claude Code was used to build this very website — from an empty folder to a running web app — in a single session.

## The Goal

The goal was simple: create a website to store and share AI-related knowledge with others. No template, no starter kit — just a conversation.

## What We Asked For

- A folder managed with **git** for version control
- A **dynamic web app** (not a static site) so content can be created and edited live
- The ability to write articles in **Markdown**

## What Claude Code Did

### 1. Chose the Stack

Based on stated preferences (Python, FastAPI, simplicity), Claude proposed:

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | SQLite via SQLAlchemy |
| Frontend | Jinja2 templates + TailwindCSS |
| Content | Markdown with syntax highlighting |

### 2. Scaffolded the Project

Claude created the full project structure:

```
ai-cotent/
├── app/
│   ├── main.py        # FastAPI entry point
│   ├── models.py      # Database models
│   ├── routes/
│   │   ├── articles.py  # REST API
│   │   └── pages.py     # HTML pages
│   └── templates/     # Jinja2 HTML
├── static/
├── requirements.txt
└── .gitignore
```

### 3. Initialized Git

Claude initialized a git repository, created a `.gitignore`, and made the first commit — after helping configure git identity.

### 4. Troubleshot the Setup

A few issues came up and were resolved together:

- **Internal PyPI conflict** — the machine was configured to use an internal package registry that required credentials. Fixed by passing `-i https://pypi.org/simple/` to pip.
- **Wrong server on port 8000** — a leftover Python file server was running on the same port. Claude identified and killed the conflicting processes, then started uvicorn correctly.
- **Git authentication** — GitHub requires a Personal Access Token (PAT) for HTTPS pushes. Claude explained how to generate one with the correct `repo` scope.

## Key Takeaways

1. **AI coding assistants work best when you describe the goal, not the steps.** Claude picked the stack, structure, and approach — the human just approved.
2. **Troubleshooting is conversational.** When things broke, describing the error was enough — no manual debugging needed.
3. **Sensitive data stays with you.** Git tokens, emails, and credentials were never shared with Claude — the human ran those commands directly in their terminal.
4. **From zero to running app in one session.** The entire scaffold, backend, frontend, and git setup was done without switching tools or writing a single line of code manually.

## The App Features

- Create, edit, and delete Markdown articles
- Live preview tab in the editor
- Tag-based organization
- Syntax-highlighted code blocks
- Clean, responsive UI with TailwindCSS
- REST API at `/api/articles`

---

## Improvement: Clickable Tag Filtering

After the initial build, the tag display was purely visual — tags appeared as badges but clicking them did nothing. A small follow-up request made them fully interactive.

### What Changed

- Tags on the home page and article pages became **clickable links**
- Each tag navigates to `/tags/{tag}`, a dedicated page listing all articles with that tag
- The active tag is **highlighted** in solid indigo on the tag filter page

### A Bug Along the Way

The first implementation had a subtle HTML bug: the article card was an `<a>` element, and the tag links were `<a>` elements inside it — nested anchors are invalid HTML. Browsers handle this unpredictably, and in this case it caused blank white boxes to appear in the layout.

The fix was to convert the article card from `<a>` to a `<div>` with an `onclick` handler, keeping the tag links as proper anchors.

### Follow-Up Questions

This improvement naturally raises some next steps worth exploring:

- **Should tags be a managed list?** Right now tags are free-text, comma-separated strings. As the knowledge base grows, typos (e.g. `LLM` vs `llm` vs `LLMs`) could fragment the tag index. A tag management system could normalize them.
- **What about a tag cloud on the home page?** Showing all existing tags at a glance would help readers explore by topic without having to read every article first.
- **Can tags support spaces?** Currently a tag like `Prompt Engineering` would work in display but the URL `/tags/Prompt Engineering` needs proper URL encoding to be reliable.

---

## Improvement: Markdown File Storage

Initially, articles were stored in a SQLite database — which worked fine locally but was gitignored, meaning the content could never be shared on GitHub.

### What Changed

- Replaced SQLAlchemy + SQLite with a file-based storage module (`app/storage.py`)
- Each article is now a `.md` file in a `content/` folder with **YAML frontmatter** for metadata
- The `content/` folder is tracked by git — articles are now version-controlled and visible on GitHub

### File Format

```markdown
---
title: My Article Title
summary: One-line description
tags: Claude, AI Coding, Python
created_at: "2026-03-12T03:49:00+00:00"
updated_at: "2026-03-12T03:49:00+00:00"
---

# Article body in Markdown...
```

### A Bug Along the Way

After migrating the storage layer, the website returned a 500 error. The root cause: timestamps stored in the YAML frontmatter as strings were being passed directly to Jinja2 templates that called `.strftime()` on them — which only works on Python `datetime` objects, not strings. Fixed by adding a `_to_datetime()` helper that parses the string back into a `datetime` before use.

### Follow-Up Questions

- **What if someone edits the `.md` file directly on GitHub?** The app picks up the changes immediately — no restart needed, since files are read on every request. This means GitHub itself becomes an editing interface.
- **Should article deletion also delete the git history?** Deleting via the UI removes the file, but the git history preserves it. This is actually a feature — deleted articles can be recovered via `git checkout`.
- **What happens with concurrent edits?** If two people edit the same article at the same time (one via the UI, one via GitHub), a git conflict could occur. For a personal knowledge base this is unlikely, but worth keeping in mind as the project grows.

---

## Improvement: CLAUDE.md for Future Sessions

As the project grew, it became useful to leave a persistent note for future Claude Code sessions — so the AI doesn't have to re-discover the architecture every time.

### What Changed

A `CLAUDE.md` file was added to the repo root. Claude Code automatically reads this file at the start of every session when opened in the project directory.

### What It Contains

- How to install dependencies and start the dev server (including the internal PyPI workaround)
- A summary of the file-based storage architecture (`app/storage.py`) — the biggest non-obvious thing in the codebase
- The article file format (YAML frontmatter + Markdown body)
- Key behaviours: slug = filename, in-memory tag filtering, server-side markdown preview endpoint

### Follow-Up Questions

- **What else belongs in CLAUDE.md?** Good candidates: common mistakes to avoid, decisions that were intentionally made a certain way, or links to external resources the AI would otherwise have to search for.
- **Should CLAUDE.md be updated as the project evolves?** Yes — treat it like living documentation. When a significant architectural decision is made, add a note explaining *why*, not just *what*.