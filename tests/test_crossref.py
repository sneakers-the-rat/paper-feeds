import pdb
import os
from .fixtures import db_tables, memory_db
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import pytest

from paper_feeds import Config
from paper_feeds.models.paper import PaperCreate
from paper_feeds.services.crossref import (
    crossref_get,
    fetch_paper_page,
    fetch_papers,
    journal_search,
    store_journal,
    populate_papers,
    last_indexed
)

def test_crossref_get_mailto():
    """
    Use the mailto parameter to be polite to crossref

    .. todo::

        make fixture to parameterize config

    .. todo::

        this one definitely needs to be vcr'd

    """
    # first should be able to not use an email if we don't want
    res = crossref_get('journals', params={'query': 'Neuron'}, email=None)
    params = parse_qs(urlparse(res.url).query)
    assert 'mailto' not in params

    # now we should add an email if asked to explicitly
    email = 'tests@example.com'
    res = crossref_get('journals', params={'query': 'Neuron'}, email=email)
    params = parse_qs(urlparse(res.url).query)
    assert params['mailto'][0] == email

    # and via .env (which should be tested separately)
    os.environ['PAPERFEEDS_CROSSREF_EMAIL'] = email
    res = crossref_get('journals', params={'query': 'Neuron'}, email=None)
    params = parse_qs(urlparse(res.url).query)
    assert params['mailto'][0] == email


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

def test_select_fields():
    """
    Only get those fields indicated by the JournalCreate class
    """
    res = fetch_paper_page('0896-6273', clean=False)
    assert res['status'] == 'ok'

    wanted_keys = set(PaperCreate.crossref_select)

    for item in res['message']['items']:
        item_keys = set(item.keys())
        # we won't get every field every time, but we shouldn't get any fields we didn't ask for
        # aka the set difference of what we got from what we wanted should be empty
        assert item_keys - wanted_keys == set()


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

@pytest.mark.timeout(20)
def test_fetch_less_than_limit():
    """Fetch less than the limit without doing an infinite loop about it"""
    for papers in fetch_papers('2666-0539', limit=1000):
        pass

def test_populate_update(memory_db):
    """
    Test that when populating papers, by default we only update the most recent papers
    since the last time we fetched papers.
    """
    journal_name = 'The Journal of Open Source Software'
    issn = '2475-9066'
    # first make sure the journal is in the DB
    store_journal(journal_search(journal_name))

    # initially we should have no papers
    last = last_indexed(issn)
    assert last is None

    first_papers = populate_papers(issn, limit=50, return_papers=True)
    # just to be sure lol
    assert len(first_papers) == 50

    # we should have gotten back the results ordered by indexed, descending
    indexed_dates = [paper.indexed for paper in first_papers]
    assert all([x>=y for x,y in zip(indexed_dates[:-1], indexed_dates[1:])])
    most_recent = max(indexed_dates)
    last = last_indexed(issn)
    assert last == most_recent

    # then when we populate again, even if we leave the limit at 1000, we should get less than that
    # we can't know in advance how many, but we should only be getting papers from the most recent day (since that's the
    # finest granularity you can filter on)
    second_papers = populate_papers(issn, limit=1000, return_papers=True)
    second_indexed_dates = [paper.indexed for paper in second_papers]
    assert len(second_papers) < 1000
    assert most_recent.date() == min(second_indexed_dates).date()


