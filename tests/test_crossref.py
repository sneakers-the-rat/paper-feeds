import pdb
from .fixtures import db_tables

import pytest

from journal_rss.services.crossref import fetch_paper_page, fetch_papers

@pytest.mark.parametrize(
    ('query'),
    (
        'Neuron'
    )
)
def test_search_journal(query):
    # TODO: this
    pass


@pytest.mark.parametrize(
    ('issn'),
    (
        '0896-6273',  # Neuron
    )
)
def test_fetch_paper_page(issn):
    # the models validating is the test passing lol
    papers = fetch_paper_page(issn)


@pytest.mark.parametrize(
    ('issn'),
    (
        '0896-6273',  # Neuron
    )
)
def test_fetch_papers(issn):
    # the models validating is the test passing lol
    for papers in fetch_papers(issn):
        pdb.set_trace()