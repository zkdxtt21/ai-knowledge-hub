from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.routes.articles import router as articles_router
from app.routes.pages import router as pages_router

app = FastAPI(title="AI Knowledge Hub")

BASE_DIR = Path(__file__).parent

app.mount("/static", StaticFiles(directory=BASE_DIR.parent / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(articles_router, prefix="/api")
app.include_router(pages_router)


@app.on_event("startup")
def on_startup():
    Path("content").mkdir(exist_ok=True)
