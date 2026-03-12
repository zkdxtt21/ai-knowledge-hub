from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import markdown

from app import storage

router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleCreate(BaseModel):
    title: str
    summary: str = ""
    content: str = ""
    tags: str = ""


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None


class ArticleOut(BaseModel):
    title: str
    slug: str
    summary: str
    content: str
    tags: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ArticleOut])
def list_articles():
    return storage.list_articles()


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(data: ArticleCreate):
    return storage.create_article(data.title, data.summary, data.content, data.tags)


@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str):
    return storage.get_article(slug)


@router.put("/{slug}", response_model=ArticleOut)
def update_article(slug: str, data: ArticleUpdate):
    return storage.update_article(slug, data.title, data.summary, data.content, data.tags)


@router.delete("/{slug}", status_code=204)
def delete_article(slug: str):
    storage.delete_article(slug)


class PreviewRequest(BaseModel):
    content: str


@router.post("/_preview")
def preview_markdown(data: PreviewRequest):
    html = markdown.markdown(data.content, extensions=["fenced_code", "tables", "toc"])
    return {"html": html}
