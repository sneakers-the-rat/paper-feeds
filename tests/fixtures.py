import pytest

from journal_rss.db import get_engine, create_tables
from journal_rss import models

@pytest.fixture(autouse=True, scope='session')
def db_tables():
    engine = get_engine()
    create_tables(engine)