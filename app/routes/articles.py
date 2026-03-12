from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import markdown

from app.models import Article, get_db, slugify

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
    id: int
    title: str
    slug: str
    summary: str
    content: str
    tags: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.updated_at.desc()).all()


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(data: ArticleCreate, db: Session = Depends(get_db)):
    slug = slugify(data.title)
    existing = db.query(Article).filter(Article.slug == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="An article with this title already exists.")
    article = Article(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        tags=data.tags,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    return article


@router.put("/{slug}", response_model=ArticleOut)
def update_article(slug: str, data: ArticleUpdate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    if data.title is not None:
        article.title = data.title
        article.slug = slugify(data.title)
    if data.summary is not None:
        article.summary = data.summary
    if data.content is not None:
        article.content = data.content
    if data.tags is not None:
        article.tags = data.tags
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{slug}", status_code=204)
def delete_article(slug: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    db.delete(article)
    db.commit()


class PreviewRequest(BaseModel):
    content: str


@router.post("/_preview")
def preview_markdown(data: PreviewRequest):
    html = markdown.markdown(data.content, extensions=["fenced_code", "tables", "toc"])
    return {"html": html}
