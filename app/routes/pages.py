from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import markdown

from app import storage

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    articles = storage.list_articles()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles})


@router.get("/articles/{slug}", response_class=HTMLResponse)
def article_page(slug: str, request: Request):
    article = storage.get_article(slug)
    html_content = markdown.markdown(article["content"], extensions=["fenced_code", "tables", "toc"])
    tags = [t.strip() for t in article["tags"].split(",") if t.strip()]
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
def edit_article(slug: str, request: Request):
    article = storage.get_article(slug)
    return templates.TemplateResponse("editor.html", {"request": request, "article": article})


@router.get("/tags/{tag}", response_class=HTMLResponse)
def tag_page(tag: str, request: Request):
    all_articles = storage.list_articles()
    articles = [a for a in all_articles if tag.lower() in [t.strip().lower() for t in a["tags"].split(",") if t.strip()]]
    return templates.TemplateResponse("tag.html", {"request": request, "tag": tag, "articles": articles})
