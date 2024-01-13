import pdb
from pathlib import Path
from typing import Annotated
from datetime import datetime

from fastapi import Depends, FastAPI, Request, Form, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlmodel import select, desc
from sqlmodel import Session

from paper_feeds.config import Config
from paper_feeds.db import create_tables, get_engine, get_session
from paper_feeds.services import crossref, journal_service
from paper_feeds.models.paper import PaperRead
from paper_feeds.models.rss import PaperRSSFeed
from paper_feeds import models
from paper_feeds.const import TEMPLATE_DIR, STATIC_DIR

from fastapi_rss import RSSResponse



app = FastAPI()
config = Config()
engine = get_engine(config)

app.mount(
    '/static',
    StaticFiles(directory=STATIC_DIR),
    name='static'
)
templates = Jinja2Templates(
    directory=TEMPLATE_DIR
)

@app.on_event("startup")
def on_startup():
    create_tables(engine)

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('pages/index.html', {"request": request})

@app.post('/search')
async def search(request: Request,
                 search: Annotated[str, Form()],
                 background: BackgroundTasks):
    """
    Search for a journal using the crossref API
    """
    results = crossref.journal_search(search)
    results = crossref.store_journal(results)

    # look for journal's homepage in the background
    background.add_task(journal_service.get_journal_homepages, journals=results)

    return templates.TemplateResponse(
        'partials/feed-list.html',
        {
            'request': request,
            'journals': results
        })

@app.get('/journals/{issn}')
async def journal_page(request: Request, issn:str):
    journal = crossref.load_journal(issn)

    # TODO: Trigger background task to update papers in journal here

    return templates.TemplateResponse(
        'pages/journal.html',
        {
            'request': request,
            'feed_id': issn,
            'journal': journal
        }
    )
    pass


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
async def paper_feeds(issn: str) -> RSSResponse:
    feed = PaperRSSFeed.from_issn(issn)
    return RSSResponse(feed)


@app.get(
    '/journals/{issn}/papers',
    response_model=list[PaperRead],
    responses= {
        200: {
            "description": "List of papers for given journal",
            "content": {
                "application/json": {},
                "text/html": {}
            }
        }
    },
         )
async def journal_papers(request: Request, issn: str, rows:int = Query(default=40, le=200), offset:int = 0):
    engine = get_engine()
    with Session(engine) as session:
        # get journal
        journal = crossref.load_journal(issn)
        # get papers
        paper_statement = select(models.Paper
             ).join(models.Journal
             ).where(models.Paper.journal_id == journal.id
             ).order_by(desc(models.Paper.published)
             ).offset(offset
             ).limit(rows)
        papers = session.exec(paper_statement).all()

    if request.headers.get('content-type',False) == 'application/json':
        return papers
    else:
        return templates.TemplateResponse(
            'partials/paper-list.html',
            {
                'request': request,
                'papers':papers
            }
        )




