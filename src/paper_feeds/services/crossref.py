import pdb
from typing import Optional, List, Generator
from datetime import datetime

import requests
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from paper_feeds import Config
from paper_feeds.models.journal import JournalCreate, Journal, JournalRead, ISSN
from paper_feeds.models.paper import PaperCreate, Paper
from paper_feeds.db import get_engine
from paper_feeds import init_logger


CROSSREF_API_URL = 'https://api.crossref.org/'
USER_AGENT = 'paper-feeds (https://github.com/sneakers-the-rat/paper-feeds)'
PAPER_TYPES = (
    'journal-article', 'book', 'book-chapter', 'book-part', 'book-section',
    'edited-book', 'proceedings-article', 'reference-book', 'dissertation',
    'report'
)
"""
Crossref types that we'll treat as a "paper"

See http://api.crossref.org/types
"""


def crossref_get(
        endpoint: str,
        params:dict,
        contact: Optional[Config] = None
) -> requests.Response:
    headers = {
        'User-Agent': USER_AGENT
    }
    if contact:
        params.update({
            'mailto': contact
        })
    return requests.get(
        CROSSREF_API_URL + endpoint,
        params=params,
        headers=headers
    )

# --------------------------------------------------
# Journals
# --------------------------------------------------

def journal_search(query:str):

    req = crossref_get(
        'journals',
        params={
            'query': query
        })
    return _clean_journal_result(req.json())

def _clean_journal_result(res: dict) -> list[JournalCreate]:
    journals = []
    for j in res['message']['items']:

        if len(j['issn-type']) > 0:
            journals.append(JournalCreate.from_crossref(j))
    return journals

def store_journal(results: list[JournalCreate]) -> list[JournalRead]:
    engine = get_engine()
    journals = []
    with Session(engine, expire_on_commit=False) as session:
        for r in results:
            statement = select(ISSN).where(ISSN.value == r.issn[0].value)
            existing_issn = session.exec(statement).first()

            if existing_issn is None:
                # create new
                db_journal = Journal.model_validate(r.model_dump())
                for issn in r.issn:
                    db_journal.issn.append(ISSN(**issn.model_dump()))
                session.add(db_journal)
                # flush here because we sometimes get duplicates in the results
                # and need to catch them on the next check
                # we'll do perf later lmao
                session.commit()

            journals.append(load_journal(r.issn[0].value))

    return journals


def load_journal(issn: str) -> JournalRead:
    engine = get_engine()
    with Session(engine) as session:
        read_statement = select(Journal
            ).options(selectinload(Journal.issn)
            ).join(ISSN
            ).where(ISSN.value == issn)
        db_journal = session.exec(read_statement).first()
        journal = JournalRead.model_validate(db_journal)
    return journal


# --------------------------------------------------
# Papers
# --------------------------------------------------


def fetch_paper_page(
        issn:str,
        rows: int = 100,
        offset: int = 0,
        since_date: Optional[datetime] = None,
        **kwargs
    ) -> list[PaperCreate]:
    # TODO: Select only fields in the model
    params = {
        'sort': 'published',
        'order': 'desc',
        'rows': rows,
        'offset': offset,
        **kwargs
    }
    if since_date:
        params['from-pub-date'] = since_date.strftime('%y-%m-%d')

    res = crossref_get(
        f'journals/{issn}/works',
        params = params
    )
    return _clean_paper_page(res.json())

def _clean_paper_page(res: dict) -> list[PaperCreate]:
    """Making a separate function in case we need to do some filtering here"""
    return [PaperCreate.from_crossref(item) for item in res['message']['items'] if item.get('type', None) in PAPER_TYPES]

def store_papers(papers: list[PaperCreate], issn: str) -> list[Paper]:
    engine = get_engine()
    ret = []
    with Session(engine) as session:
        # get journal that stores these papers
        journal_statement = select(Journal).join(ISSN).where(ISSN.value == issn)
        journal = session.exec(journal_statement).first()

        for paper in papers:
            # get already existing paper
            existing_statement = select(Paper).where(Paper.doi == paper.doi)
            existing = session.exec(existing_statement).first()
            if existing is not None:
                # update
                store_paper = existing
                store_paper.journal = journal
                # this is how the docs say to do it ig
                for key, val in paper.model_dump(exclude_unset=True).items():
                    setattr(store_paper, key, val)

            else:
                store_paper = Paper.model_validate(paper)
                store_paper.journal = journal

            session.add(store_paper)
            session.commit()
            session.refresh(store_paper)
            ret.append(store_paper)

    return ret

def fetch_papers(issn: str, limit: int = 1000, rows=100) -> Generator[list[Paper],None, None]:
    # get the most recent paper to subset paging
    # then get pages and write them as we get the pages
    # then return the completed sql models

    # TODO: Only get papers since the last time we updated
    got_papers = fetch_paper_page(issn, rows)
    stored_papers = store_papers(got_papers, issn)
    yield stored_papers

    n_papers = len(got_papers)
    while n_papers < limit and len(got_papers) == rows:
        get_rows = min(limit-n_papers, rows)
        got_papers = fetch_paper_page(issn, get_rows, n_papers)
        stored_papers = store_papers(got_papers, issn)
        n_papers += len(got_papers)
        yield stored_papers

def populate_papers(issn: str, limit: int = 1000, rows=100):
    """
    Background task for :func:`.fetch_papers`
    """
    logger = init_logger()
    logger.debug('fetching papers for ISSN %s', issn)
    fetcher = fetch_papers(issn, limit, rows)
    fetched = 0

    while True:
        try:
            papers = next(fetcher)
            fetched += len(papers)
            logger.debug('fetched %d papers', fetched)
        except StopIteration:
            break

    logger.debug('completed paper fetch for %s', issn)
