from pathlib import Path
from datetime import datetime, timezone
from fastapi import HTTPException
import frontmatter
import re

CONTENT_DIR = Path("content")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


def _path(slug: str) -> Path:
    return CONTENT_DIR / f"{slug}.md"


def _to_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        value = value.strip('"')
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return datetime.now(timezone.utc)


def _parse(path: Path) -> dict:
    post = frontmatter.load(str(path))
    slug = path.stem
    return {
        "slug": slug,
        "title": post.get("title", slug),
        "summary": post.get("summary", ""),
        "tags": post.get("tags", ""),
        "content": post.content,
        "created_at": _to_datetime(post.get("created_at", datetime.now(timezone.utc))),
        "updated_at": _to_datetime(post.get("updated_at", datetime.now(timezone.utc))),
    }


def _write(slug: str, title: str, summary: str, content: str, tags: str,
           created_at: datetime, updated_at: datetime) -> None:
    post = frontmatter.Post(
        content,
        title=title,
        summary=summary,
        tags=tags,
        created_at=created_at,
        updated_at=updated_at,
    )
    _path(slug).write_text(frontmatter.dumps(post), encoding="utf-8")


def list_articles() -> list[dict]:
    articles = [_parse(p) for p in sorted(CONTENT_DIR.glob("*.md"))]
    return sorted(articles, key=lambda a: a["updated_at"], reverse=True)


def get_article(slug: str) -> dict:
    path = _path(slug)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Article not found.")
    return _parse(path)


def create_article(title: str, summary: str, content: str, tags: str) -> dict:
    slug = slugify(title)
    if _path(slug).exists():
        raise HTTPException(status_code=409, detail="An article with this title already exists.")
    now = datetime.now(timezone.utc)
    _write(slug, title, summary, content, tags, now, now)
    return get_article(slug)


def update_article(slug: str, title: str | None, summary: str | None,
                   content: str | None, tags: str | None) -> dict:
    existing = get_article(slug)
    new_title = title if title is not None else existing["title"]
    new_slug = slugify(new_title)
    new_summary = summary if summary is not None else existing["summary"]
    new_content = content if content is not None else existing["content"]
    new_tags = tags if tags is not None else existing["tags"]
    updated_at = datetime.now(timezone.utc)

    if new_slug != slug:
        _path(slug).unlink()
    _write(new_slug, new_title, new_summary, new_content, new_tags,
           existing["created_at"], updated_at)
    return get_article(new_slug)


def delete_article(slug: str) -> None:
    path = _path(slug)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Article not found.")
    path.unlink()
