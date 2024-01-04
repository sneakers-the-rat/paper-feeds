import pytest
import shutil
from pathlib import Path

import requests_cache

def pytest_addoption(parser):
    parser.addoption(
        '--persist-http-cache',
        action='store_true',
        help="Don't delete the requests_cache .sqlite file after completing tests"
    )

@pytest.fixture(scope="session", autouse=True)
def patch_requests_cache(pytestconfig):
    """
    Save crossref some stress if we end up doing a lot of the same query,
    but maybe don't do this in prod until we can be more principled about it.

    The cache should be destroyed and recreated each session
    """
    cache_file = Path('./tests/journal-rss-tests.sqlite')
    requests_cache.install_cache(
        str(cache_file),
        backend='sqlite',
        urls_expire_after = {
            'localhost': requests_cache.DO_NOT_CACHE
        }
    )
    requests_cache.clear()
    yield
    # delete cache file unless we have requested it to persist for inspection
    if not pytestconfig.getoption('--persist-http-cache'):
        cache_file.unlink(missing_ok=True)