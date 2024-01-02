import pdb
from typing import Optional, List, Generator
from datetime import datetime

import requests
from sqlmodel import Session, select

from journal_rss import Config
from journal_rss.models.journal import JournalCreate, Journal, ISSN
from journal_rss.models.paper import PaperCreate, Paper
from journal_rss.const import SCIHUB_URL
from journal_rss.db import get_engine


CROSSREF_API_URL = 'https://api.crossref.org/'
USER_AGENT = 'journal-rss (https://github.com/sneakers-the-rat/journal-rss)'

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

def _simplify_author(author) -> str:
    """
    'author': [{'affiliation': [],
         'family': 'FirstName',
         'given': 'LastName',
         'sequence': 'first'}],
    """
    names = []
    for name in author:
        if name.get('name', None):
            names.append(name.get('name'))
            continue

        # don't use get bc want to fail to find out what possible values are
        if name['sequence'] in ('first', 'additional'):
            name_parts = []
            if name.get('given', None):
                name_parts.append(name['given'])
            if name.get('family', None):
                name_parts.append(name['family'])

            names.append(' '.join(name_parts))
        else:
            raise ValueError(f'unhandled name sequence {name["sequence"]}')

    return ', '.join(names)

def _simplify_datetime(date: dict) -> Optional[datetime]:
    """
    date = {
        'date-parts': [[2023, 12, 21]],
        'date-time': '2023-12-21T00:07:03Z',
        'timestamp': 1703117223000},
    }

    :param date:
    :return:
    """
    if date is None:
        return None

    if date.get('timestamp', None):
        timestamp = float(date.get('timestamp'))
        if timestamp > 1_000_000_000_000:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp)
    elif date.get('date-time', None):
        return datetime.fromisoformat(date.get('date-time'))
    elif date.get('date-parts', None):
        parts = date.get('date-parts')
        if isinstance(parts[0], list):
            parts = parts[0]
        if len(parts) == 2:
            # add the first day of the month
            parts.append(1)
        return datetime(*parts)
    else:
        raise ValueError(f"Cant handle date: {date}")

def _unwrap_list(input: list | str, sep=', ') -> Optional[str]:
    if isinstance(input, str):
        return input
    elif input is None:
        return None
    else:
        return sep.join(input)


def _clean_paper_page(res:dict) -> list[PaperCreate]:
    items = res['message']['items']
    papers = []
    for item in items:
        # TODO: Make this a fieldvalidator that converts names and applies functions
        papers.append(PaperCreate(
            doi = item['DOI'],
            url = item['URL'],
            author=_simplify_author(item['author']),
            created = _simplify_datetime(item['created']),
            deposited = _simplify_datetime(item['deposited']),
            edition_number= item.get('edition-number', None),
            indexed = _simplify_datetime(item['indexed']),
            issue = item.get('issue', None),
            issued = _simplify_datetime(item.get('issued', None)),
            page = item.get('page', None),
            posted = _simplify_datetime(item.get('posted', None)),
            published = _simplify_datetime(item.get('published', None)),
            published_print = _simplify_datetime(item.get('published-print', None)),
            published_online = _simplify_datetime(item.get('published-online', None)),
            publisher = item['publisher'],
            reference_count= item.get('reference-count', None),
            references_count = item.get('references-count', None),
            short_title = item.get('short-title', None),
            source = item.get('source', None),
            subject = ', '.join(item.get('subject', [''])),
            title = _unwrap_list(item['title']),
            type = item['type'],
            volume = item.get('volume', None),
            scihub = SCIHUB_URL + item['DOI']
        ))
    return papers

def fetch_paper_page(
        issn:str,
        rows: int = 100,
        offset: int = 0,
        since_date: Optional[datetime] = None
    ) -> list[PaperCreate]:
    # TODO: Select only fields in the model
    params = {
        'sort': 'published',
        'order': 'desc',
        'rows': rows,
        'offset': offset
    }
    if since_date:
        params['from-pub-date'] = since_date.strftime('%y-%m-%d')

    res = crossref_get(
        f'journals/{issn}/works',
        params = params
    )
    return _clean_paper_page(res.json())

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
    while n_papers < limit:
        get_rows = min(limit-n_papers, rows)
        got_papers = fetch_paper_page(issn, get_rows, n_papers)
        stored_papers = store_papers(got_papers, issn)
        yield stored_papers


