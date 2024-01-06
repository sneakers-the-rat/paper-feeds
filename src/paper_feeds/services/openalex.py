import requests

from paper_feeds.config import config

OPENALEX_API_URL = 'https://api.openalex.org/'
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
