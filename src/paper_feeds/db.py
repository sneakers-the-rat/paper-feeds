from typing import Optional, TYPE_CHECKING
import importlib.resources

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from alembic.config import Config as AlembicConfig
from alembic import command
from alembic.util.exc import CommandError

from paper_feeds import Config
from paper_feeds.decorators import singleton
from paper_feeds.exceptions import DBMigrationError
# all models need to be imported when creating tables
from paper_feeds import models

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
    """
    Create tables and stamps with an alembic version

    Args:
        engine:
        config:

    References:
        - https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
    """
    if config is None:
        config = Config()

    SQLModel.metadata.create_all(engine)
    # check version here since creating the table is the same action as
    # ensuring our migration metadata is correct!
    ensure_alembic_version(engine)


def ensure_alembic_version(engine):
    """
    Make sure that our database is correctly stamped and migrations are applied.

    Raises:
        :class:`.exceptions.DBMigrationError` if migrations need to be applied!
    """
    # Handle database migrations and version stamping!
    alembic_config = get_alembic_config()

    command.ensure_version(alembic_config)
    version = alembic_version(engine)

    # Check to see if we are up to date
    if version is None:
        # haven't been stamped yet, but we know we are
        # at the head since we just made the db.
        command.stamp(alembic_config, 'head')
    else:
        try:
            command.check(alembic_config)
        except CommandError:
            # don't automatically migrate since it could be destructive
            raise DBMigrationError('Database needs to be migrated! Run paper-feeds migrate')


def get_alembic_config() -> AlembicConfig:
    return AlembicConfig(str(importlib.resources.files('paper_feeds') / 'migrations' / 'alembic.ini'))

def alembic_version(engine: 'Engine') -> Optional[str]:
    """
    for some godforsaken reason alembic's command for getting the
    db version ONLY PRINTS IT and does not return it.

    "fuck it we'll do it live"

    Args:
        engine (:class:`sqlalchemy.Engine`):

    Returns:
        str: Alembic version revision
        None: if there is no version yet!
    """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()

    if version is not None:
        version = version[0]

    return version
