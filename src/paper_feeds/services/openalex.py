import requests

from paper_feeds.config import config

OPENALEX_API_URL = 'https://api.openalex.org/'
SOURCES_ENDPOINT = 'sources'
USER_AGENT = 'paper-feeds (https://github.com/sneakers-the-rat/paper-feeds)'


def _openalex_get(endpoint: str, params: dict) -> requests.Response:
    # let OpenAlex know who you are, so you can enter their polite pool
    # https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#authentication
    if config.crossref_email:
        params['mailto'] = config.crossref_email

    headers = {'User-Agent': USER_AGENT}

    # send out request to API
    return requests.get(OPENALEX_API_URL + endpoint,
                        params=params,
                        headers=headers)


def get_journal_homepages(issns: list[str]) -> dict:
    """ Get homepage urls for a bunch of ISSNs. """

    # minimize API calls using approach outlined in OpenAlex blog
    # https://blog.ourresearch.org/fetch-multiple-dois-in-one-openalex-api-request/
    slice_size = 50
    issn_homepage_map = {}
    for i in range(0, len(issns), slice_size):
        issns_slice = issns[i:i + slice_size]
        pipe_separated_issns = "|".join(issns_slice)
        params = {'select': 'issn,homepage_url',
                  'per_page': slice_size,
                  'filter': f'issn:{pipe_separated_issns}'}

        response = _openalex_get(SOURCES_ENDPOINT, params)

        if response.status_code == 200:
            results = response.json().get('results', [])
            issn_homepage_map = {**issn_homepage_map, **_index_issns(results)}

    return issn_homepage_map


def _index_issns(journals: list[str]) -> dict:
    """ Create map: issn -> homepage_url for quick lookup """
    return {issn: journal.get('homepage_url', None)
            for journal in journals
            for issn in journal.get('issn', [])}
