from urllib.parse import urlparse, parse_qs

import pytest

from paper_feeds.services.openalex import _openalex_get, get_journal_homepages


def test_most_basic_api_call():
    """
    Test bare call to the OpenAlex API (no endpoint or params specified).
    """
    response = _openalex_get("", {}, None)
    assert response.status_code == 200

    # Assert header for 'User agent' was included
    user_agent_header = response.request.headers.get("User-Agent", None)
    assert "paper-feeds" in user_agent_header

    # Assert email was not set (default in config is None)
    params = parse_qs(urlparse(response.url).query)
    assert "mailto" not in params


def test_email_included_in_params():
    """
    Test setting of 'mailto' in query parameters if parameter exists in config.
    """
    email = "tests@example.com"
    response = _openalex_get("", {}, email)
    params = parse_qs(urlparse(response.url).query)
    assert params["mailto"][0] == email


@pytest.mark.parametrize(
    "issn,homepage",
    [("0024-2160", "https://academic.oup.com/library"), ("1758-6909", None)],
)
def test_get_journal_homepages(issn, homepage):
    issn_homepage_map = get_journal_homepages([issn], None)
    assert issn_homepage_map[issn] == homepage
