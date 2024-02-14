import pytest

from sqlmodel import create_engine, SQLModel
from sqlalchemy import Engine

from paper_feeds.db import get_engine, create_tables
from paper_feeds import models
from paper_feeds.services.crossref import journal_search, store_journal, populate_papers


@pytest.fixture(autouse=True, scope="session")
def db_tables():
    """
    Persistent db for use with human-in-the-loop testing and debugging ;).
    """
    engine = get_engine()
    create_tables(engine)
    return engine


@pytest.fixture(scope="session")
def base_journal_data(db_tables):
    """
    Example journal data used when not testing the journal querying functionality.
    Should we hardcode this instead?

    .. todo::

        Clean this up so we can use it as a function-scoped fixture
    """
    journals = journal_search("Neuron")
    _ = store_journal(journals)


@pytest.fixture(scope="session")
def base_paper_data(db_tables):
    """
    Similar to ^ but with papers
    """
    populate_papers("0896-6273", limit=100)


@pytest.fixture(scope="session")
def base_data(base_journal_data, base_paper_data):
    """
    Collects the other kinds of base data
    """
    pass


@pytest.fixture(scope="function")
def memory_db() -> Engine:
    """
    Fresh, in-memory SQL database for unit testing
    """
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    old_engine = getattr(get_engine, "_instance", None)

    get_engine._instance = engine
    yield engine

    # restore old engine
    get_engine._instance = old_engine
