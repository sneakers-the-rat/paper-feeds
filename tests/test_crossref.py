import pdb
from .fixtures import db_tables, memory_db

import pytest

from paper_feeds.services.crossref import fetch_paper_page, fetch_papers, journal_search, store_journal

@pytest.mark.parametrize(
    'query,issn',
    [
        ('Neuron', '0896-6273')
    ]
)
def test_search_journal(query, issn, memory_db):
    res = journal_search(query)
    # check that we got the expected journal from the query
    journals = [j for j in res if j.title == query]
    assert len(journals) == 1
    # we don't validate model here because pydantic does that for us!

    # validate that we can store journals, returning a hydrated set of journal objects
    db_journals = store_journal(journals)
    assert len(journals) == len(db_journals)

    # main check here is that we get the linked ISSN object back along with the main model
    test_journal = [j for j in db_journals if j.title == query][0]
    issns = [issn.value for issn in test_journal.issn]
    assert issn in issns

    # then check if we still get fully hydrated models when we already have the models in the db
    db_journals_2 = store_journal(journals)
    assert len(journals) == len(db_journals_2)
    test_journal = [j for j in db_journals_2 if j.title == query][0]
    issns = [issn.value for issn in test_journal.issn]
    assert issn in issns


@pytest.mark.parametrize(
    ('issn'),
    (
        '0896-6273',  # Neuron
    )
)
def test_fetch_paper_page(issn):
    # the models validating is the test passing lol
    papers = fetch_paper_page(issn)

def test_filter_non_papers():
    """
    Tests issues:
    - https://github.com/sneakers-the-rat/paper-feeds/issues/16
    """
    # result known to be a `journal` type
    journal_item = fetch_paper_page('1674-9251', rows=1, filter='type:journal')
    assert len(journal_item) == 0



@pytest.mark.parametrize(
    ('issn,limit'),
    (
            ('0896-6273', 200),  # Neuron
    )
)
def test_fetch_papers(issn, limit):
    # the models validating is the test passing for now
    all_papers = []
    for papers in fetch_papers(issn, limit=limit):
        all_papers.extend(papers)
    assert len(all_papers) == limit

@pytest.mark.timeout(10)
def test_fetch_less_than_limit():
    """Fetch less than the limit without doing an infinite loop about it"""
    for papers in fetch_papers('2666-0539', limit=1000):
        pass