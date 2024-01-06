from urllib.parse import urlparse, parse_qs

from paper_feeds.config import config
from paper_feeds.services.openalex import _openalex_get


def test_most_basic_api_call():
    """
    Test bare call to the OpenAlex API (no endpoint or params specified).
    """
    response = _openalex_get('', {})
    assert response.status_code == 200

    # Assert header for 'User agent' was included
    user_agent_header = response.request.headers.get('User-Agent', None)
    assert 'paper-feeds' in user_agent_header

    # Assert email was not set (default in config is None)
    params = parse_qs(urlparse(response.url).query)
    assert 'mailto' not in params


def test_email_included_in_params(mocker):
    """
    Test setting of 'mailto' in query parameters if parameter exists in config.
    """
    # set config parameter using mock
    email = 'tests@example.com'
    mocker.patch.object(config, "crossref_email", new=email)

    # Assert email was set to value in config
    response = _openalex_get('', {})
    params = parse_qs(urlparse(response.url).query)
    assert params['mailto'][0] == email
