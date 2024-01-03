import pdb
from pathlib import Path
from typing import Annotated
from datetime import datetime

from fastapi import Depends, FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlmodel import select

# from sqlalchemy.orm import Session
from sqlmodel import Session

from journal_rss.config import Config
from journal_rss.db import create_tables, get_engine, get_session
from journal_rss.services import crossref
from journal_rss.models import api
from journal_rss.models.rss import PaperRSSFeed
from journal_rss import models

from fastapi_rss import RSSResponse



app = FastAPI()
config = Config()
engine = get_engine(config)

app.mount('/static', StaticFiles(
    directory=(Path(__file__).parents[1] / 'static').resolve()), name='static')
templates = Jinja2Templates(
    directory=(Path(__file__).parents[1]  / 'templates').resolve()
)

@app.on_event("startup")
def on_startup():
    create_tables(engine)

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.post('/search')
async def search(request: Request, search: Annotated[str, Form()]):
    """
    Search for a journal using the crossref API
    """
    results = crossref.journal_search(search)
    results = crossref.store_journal(results)

    return templates.TemplateResponse(
        'partials/feed-list.html',
        {
            'request': request,
            'journals': results
        })

@app.post('/journals/{issn}/feed')
async def make_feed(
        feed_id: Annotated[str, Form()],
        request: Request,
        background: BackgroundTasks
):
    """
    Enable the "feed" attribute for the given journal and trigger an initial population

    Don't expose the full journal model to CRUD, the only field we want to be able to update
    is `feed`, and the only thing we want to do to it is set it to ``True``
    """
    with Session(engine) as session:
        statement = select(models.Journal).join(models.ISSN).where(models.ISSN.value == feed_id)
        journal = session.exec(statement).one()
        if journal is None:
            # TODO: Handle creating journal entries from here
            return

        journal.feed = True
        journal.feed_created = datetime.utcnow()
        session.add(journal)
        session.commit()

    # start populating the feed
    background.add_task(crossref.populate_papers, issn=feed_id)

    return templates.TemplateResponse(
        'partials/rss-button.html',
        {
            'feed_type': 'journals',
            'feed_id': feed_id,
            'request': request,
        })

@app.get('/journals/{issn}/rss')
async def journal_rss(issn: str) -> RSSResponse:
    feed = PaperRSSFeed.from_issn(issn)
    return RSSResponse(feed)




