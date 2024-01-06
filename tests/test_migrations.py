"""
These tests are just for our functions that handle migrations,
the actual migrations themselves are tested by pytest-alembic
https://pytest-alembic.readthedocs.io/
and imported here
"""

import pytest
from alembic import command

from .fixtures import memory_db, db_tables

from paper_feeds.db import alembic_version, get_alembic_config

from pytest_alembic.tests import (
    test_model_definitions_match_ddl,
    test_single_head_revision,
    test_up_down_consistency,
    test_upgrade,
)

def test_alembic_version(db_tables):
    """
    Ensure our alembic version function gets the alembic version!
    """
    alembic_config = get_alembic_config()

    command.ensure_version(alembic_config, sql=True)

    command.stamp(alembic_config, None)
    assert alembic_version(db_tables) is None
    command.stamp(alembic_config, 'head')
    version = alembic_version(db_tables)
    # alembic doesn't let us get the actual version number to compare against too easily,
    # so if we've got a string that's good enough for now.
    assert isinstance(version, str)
