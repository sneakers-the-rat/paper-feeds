import pdb
from typing import Optional, List
from datetime import datetime

import requests

from journal_rss import Config
from journal_rss.models.journal import JournalCreate
from journal_rss.models.paper import PaperCreate, Paper


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

def _clean_paper_page(res) -> list[PaperCreate]:
    raise NotImplementedError()

def fetch_paper_page(
        issn:str,
        rows: int = 20,
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
    return _clean_paper_page(res)

def fetch_papers(issn: str) -> list[Paper]:
    # get the most recent paper to subset paging
    # then get pages and write them as we get the pages
    # then return the completed sql models
    pass