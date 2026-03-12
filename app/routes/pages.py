from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
import markdown

from app.models import Article, get_db

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.updated_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles})


@router.get("/articles/{slug}", response_class=HTMLResponse)
def article_page(slug: str, request: Request, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    html_content = markdown.markdown(article.content, extensions=["fenced_code", "tables", "toc"])
    tags = [t.strip() for t in article.tags.split(",") if t.strip()]
    return templates.TemplateResponse("article.html", {
        "request": request,
        "article": article,
        "html_content": html_content,
        "tags": tags,
    })


@router.get("/new", response_class=HTMLResponse)
def new_article(request: Request):
    return templates.TemplateResponse("editor.html", {"request": request, "article": None})


@router.get("/edit/{slug}", response_class=HTMLResponse)
def edit_article(slug: str, request: Request, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    return templates.TemplateResponse("editor.html", {"request": request, "article": article})


@router.get("/tags/{tag}", response_class=HTMLResponse)
def tag_page(tag: str, request: Request, db: Session = Depends(get_db)):
    all_articles = db.query(Article).order_by(Article.updated_at.desc()).all()
    articles = [a for a in all_articles if tag.lower() in [t.strip().lower() for t in a.tags.split(",") if t.strip()]]
    return templates.TemplateResponse("tag.html", {"request": request, "tag": tag, "articles": articles})
