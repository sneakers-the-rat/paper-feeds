import pytest
from sqlmodel import Session

from paper_feeds.models import ISSN, Journal
from paper_feeds.repositories.journal_repository import (
    update_journal_homepages,
    get_journal_by_issn)


@pytest.fixture(scope='function')
def sample_journal(memory_db):
    """Create and insert a sample journal into the database."""

    with Session(memory_db) as session:
        # Create sample journal
        journal = Journal(
            title="Sample Journal",
            publisher="Sample Publisher",
            recent_paper_count=5
        )

        # Add ISSN to the journal
        issn = ISSN(type="print", value="1234-5678")
        journal.issn.append(issn)

        # Store journal in DB
        session.add(journal)
        session.commit()

        yield journal


def test_get_journal_by_issn(memory_db, sample_journal):
    """Test the get_journal_by_issn method with an in-memory database."""
    journal_expected = sample_journal
    issn = journal_expected.issn[0].value

    with (Session(memory_db) as session):
        journal_from_db = get_journal_by_issn(session, issn)

        # verify that the sample_journal was retrieved from db
        assert journal_from_db is not None
        assert journal_from_db.title == journal_expected.title
        assert journal_from_db.issn[0].value == issn


def test_update_journal_homepages(memory_db, sample_journal):
    """Test the update_journal_homepages method with an in-memory database."""

    journal_expected = sample_journal
    issn = journal_expected.issn[0].value
    homepage = "http://updated-homepage.com"

    with Session(memory_db) as session:
        # dictionary {issn: homepage_url}
        updates = {issn: homepage}
        update_journal_homepages(session, updates)

        # verify that the homepage URL for the sample journal was updated
        journal_from_db = get_journal_by_issn(session, issn)
        assert journal_from_db.issn[0].value == issn
        assert journal_from_db.homepage_url == homepage
