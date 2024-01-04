"""
All models used in the DB should be imported here so they are created by
:func:`.db.create_tables`
"""
from sqlmodel import SQLModel
from journal_rss.models.journal import Journal, ISSN
from journal_rss.models.paper import Paper

