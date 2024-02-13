import pdb
from typing import Optional, List, Generator, overload, Literal
from datetime import datetime, timezone

import requests
from sqlmodel import Session, select, desc
from sqlalchemy.orm import selectinload

from paper_feeds import Config
from paper_feeds.models.journal import JournalCreate, Journal, JournalRead, ISSN
from paper_feeds.models.paper import PaperCreate, Paper, PaperRead
from paper_feeds.db import get_engine
from paper_feeds import init_logger
from paper_feeds.exceptions import FetchError


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
        params: dict,
        email: Optional[str] = None
) -> requests.Response:
    """
    .. todo::

        Document this

    Args:
        endpoint (str): Endpoint appended to :data:`.CROSSREF_API_URL`
        params (dict): Query parameters
        email (str): Email used to be `polite to crossref <https://github.com/CrossRef/rest-api-doc#good-manners--more-reliable-service>`_
            If ``None`` , use ``crossref_email`` set in :class:`.Config`

    Returns:
        :class:`requests.Response`
    """
    headers = {
        'User-Agent': USER_AGENT
    }
    if email is None:
        email = Config().crossref_email

    if email:
        params.update({
            'mailto': email
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
        if db_journal is None:
            raise ValueError(f"Journal with issn {issn} is not in the database!")
        journal = JournalRead.model_validate(db_journal)
    return journal


# --------------------------------------------------
# Papers
# --------------------------------------------------

def fetch_paper_page(
        issn:str,
        rows: int = 100,
        offset: int = 0,
        from_index_date: Optional[datetime] = None,
        clean:bool = True,
        **kwargs
    ) -> list[PaperCreate] | dict:
    """

    Args:
        issn (str): ISSN of journal (any ISSN for a given journal gives the same results)
        rows (int): Number of items to fetch
        offset (int): Number of items to offset from the most recent (sorted by published date)
        from_index_date (:class:`datetime.datetime`): Optional: Get papers only published after this date
        clean (bool): If ``True`` (default), cast as :class:`.PaperCreate` before returning.
            Otherwise, return raw result from the `GET` request. Useful mostly for testing
    """
    params = {
        'sort': 'indexed',
        'order': 'desc',
        'rows': rows,
        'offset': offset,
        'select': ','.join(PaperCreate.crossref_select),
        **kwargs
    }
    # explicitly passed kwargs override defaults
    params.update(kwargs)
    if from_index_date:
        params['filter'] = 'from-index-date:' + from_index_date.strftime('%Y-%m-%d')

    res = crossref_get(
        f'journals/{issn}/works',
        params = params
    )
    res_json = res.json()
    if res_json['status'] != 'ok':
        raise FetchError(f"Error fetching from crossref! Got error message back:\n{res_json['message']}")

    if clean:
        return _clean_paper_page(res_json)
    else:
        return res_json

def _clean_paper_page(res: dict) -> list[PaperCreate]:
    """Making a separate function in case we need to do some filtering here"""
    return [PaperCreate.from_crossref(item) for item in res['message']['items'] if item.get('type', None) in PAPER_TYPES]

def store_papers(papers: list[PaperCreate], issn: str) -> list[PaperRead]:
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
            # TODO: get the JournalRead object too
            read = PaperRead.model_validate(store_paper)
            ret.append(read)

    return ret

def fetch_papers(issn: str, limit: int = 1000, rows:int=100, offset:int=0, **kwargs) -> Generator[list[Paper],None, None]:
    # get the most recent paper to subset paging
    # then get pages and write them as we get the pages
    # then return the completed sql models=
    got_papers = fetch_paper_page(issn, rows, offset, **kwargs)
    stored_papers = store_papers(got_papers, issn)
    yield stored_papers

    n_papers = len(got_papers)
    while n_papers < limit and len(got_papers) == rows:
        get_rows = min(limit-n_papers, rows)
        got_papers = fetch_paper_page(issn, get_rows, offset+n_papers, **kwargs)
        stored_papers = store_papers(got_papers, issn)
        n_papers += len(got_papers)
        yield stored_papers

def populate_papers(
        issn: str,
        limit: int = 1000,
        rows=100,
        force:bool=False,
        return_papers:bool=False,
        **kwargs) -> Optional[list[Paper]]:
    """
    Background task for :func:`.fetch_papers`

    By default, only get papers newer than the last indexed date for this issn

    Args:
        issn (str): ISSN of journal to fetch for
        limit (int): Total number of papers to fetch
        rows (int): Number of papers to fetch in each page
        force (bool): if ``True``, ignore previously stored papers and fetch everything
        return_papers (bool): If ``True`` , Return fetched papers. If ``False``, return ``None`` - mostly useful for testing,
            since everywhere else :func:`.fetch_papers` is more useful
        **kwargs:

    Returns:

    """
    logger = init_logger()
    logger.debug('fetching papers for ISSN %s', issn)

    rows = min(rows, limit)

    all_papers = []
    if force:
        update_from = None
    else:
        update_from = last_indexed(issn)
    fetcher = fetch_papers(issn, limit, rows, from_index_date=update_from, **kwargs)
    fetched = 0

    while True:
        try:
            papers = next(fetcher)
            fetched += len(papers)
            if return_papers:
                all_papers.extend(papers)
            logger.debug('fetched %d papers', fetched)
        except StopIteration:
            break

    logger.debug('completed paper fetch for %s', issn)
    if return_papers:
        return all_papers


def last_indexed(issn:str) -> Optional[datetime]:
    """
    Get the last indexed timestamp from the most recent paper for a given issn.
    """
    # first try and get the most recent paper from this ISSN, if we have any
    engine = get_engine()
    with Session(engine) as session:
        journal = load_journal(issn)
        existing_statement = select(Paper).join(Journal
            ).where(Paper.journal_id == journal.id
            ).order_by(desc(Paper.indexed)
            ).limit(1)
        existing = session.exec(existing_statement).first()
    if existing is None:
        most_recent = None
    else:
        most_recent = existing.indexed
    return most_recent
