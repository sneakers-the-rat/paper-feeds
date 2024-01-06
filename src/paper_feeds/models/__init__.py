"""
All models used in the DB should be imported here so they are created by
:func:`.db.create_tables`
"""
from sqlmodel import SQLModel
from paper_feeds.models.journal import Journal, ISSN
from paper_feeds.models.paper import Paper

