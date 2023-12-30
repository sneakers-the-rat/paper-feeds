import pdb
from typing import Optional

import requests

from journal_rss import Config
from journal_rss.models.journal import JournalCreate


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
