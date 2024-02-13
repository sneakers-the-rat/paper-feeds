from typing import Optional

import requests

OPENALEX_API_URL = 'https://api.openalex.org/'
SOURCES_ENDPOINT = 'sources'
USER_AGENT = 'paper-feeds (https://github.com/sneakers-the-rat/paper-feeds)'


def _openalex_get(endpoint: str, params: dict,
                  email: Optional[str]) -> requests.Response:
    """
    Sends a GET request to the OpenAlex API endpoint with optional parameters.

    Args:
        endpoint (str): The API endpoint to query.
        params (dict): Optional query parameters to include in the request.
        email (Optional[str]): An optional email address used to access OpenAlex`s polite pool.

    Returns:
        requests.Response: The response object containing the data.

    Raises:
        requests.RequestException: If a network-related issue occurs during the request.
    """

    # let OpenAlex know who you are, so you can enter their polite pool
    # https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#authentication
    if email:
        params['mailto'] = email

    headers = {'User-Agent': USER_AGENT}

    # send out request to API
    return requests.get(OPENALEX_API_URL + endpoint,
                        params=params,
                        headers=headers)


def get_journal_homepages(issns: list[str], email: Optional[str]) -> dict:
    """
    Get homepage URLs for a list of ISSNs.

    Args:
        issns (list of str): A list of ISSNs for which homepage URLs are requested.
        email (Optional[str]): An optional email address used to access OpenAlex`s polite pool.

    Returns:
        dict: A dictionary mapping ISSNs to their corresponding homepage URLs.
    """

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

        response = _openalex_get(SOURCES_ENDPOINT, params, email)

        if response.status_code == 200:
            results = response.json().get('results', [])
            issn_homepage_map = {**issn_homepage_map, **_index_issns(results)}

    return issn_homepage_map


def _index_issns(journals: list[str]) -> dict:
    """
    Create a mapping of ISSN to homepage URL for quick lookup.

    Args:
        journals (list of dict): A list of journal dictionaries.

    Returns:
        dict: A dictionary mapping ISSNs to their corresponding homepage URLs.
    """

    return {issn: journal.get('homepage_url', None)
            for journal in journals
            for issn in journal.get('issn', [])}
