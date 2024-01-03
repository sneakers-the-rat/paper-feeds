import pytest

from sqlmodel import create_engine, SQLModel
from sqlalchemy import Engine

from journal_rss.db import get_engine, create_tables
from journal_rss import models

@pytest.fixture(autouse=True, scope='session')
def db_tables():
    """Persistent db for use with human-in-the-loop testing and debugging ;)"""
    engine = get_engine()
    create_tables(engine)

@pytest.fixture(scope='function')
def memory_db() -> Engine:
    """
    Fresh, in-memory SQL database for unit testing
    """
    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)
    old_engine = getattr(get_engine, '_instance', None)

    get_engine._instance = engine
    yield engine

    # restore old engine
    get_engine._instance = old_engine