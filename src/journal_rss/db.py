from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker

from journal_rss import Config
from journal_rss.decorators import singleton
# all models need to be imported when creating tables
from journal_rss import models

if TYPE_CHECKING:
    from sqlalchemy.future.engine import Engine

@singleton
def get_engine(config: Optional[Config] = None) -> 'Engine':
    """
    According to the sqlmodel docs, there should be
    one engine per application, and one should use it to
    open sessions for each function/context.
    """
    if config is None:
        config = Config()

    engine = create_engine(config.sqlite_path)
    return engine


def get_session(engine: Optional['Engine'] = None):
    if engine is None:
        engine = get_engine()
    maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        db = maker()
        yield db
    finally:
        db.close()

def create_tables(
        engine: 'Engine',
        config:Optional[Config] = None
    ):
    if config is None:
        config = Config()

    SQLModel.metadata.create_all(engine)