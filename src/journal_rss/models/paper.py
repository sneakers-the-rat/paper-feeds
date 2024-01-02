import sys
import typing
from typing import Optional, Union, Tuple, List, Dict, Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from journal_rss.models import Journal


from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship

class PaperBase(SQLModel):
    """https://api.crossref.org/swagger-ui/index.html#model-Work"""
    doi: str
    title: str
    subtitle: Optional[str] = None
    short_title: Optional[str] = None
    author: str
    type: str
    abstract: Optional[str] = None

    # indexing
    publisher: str
    edition_number: Optional[str] = None
    issue: Optional[str] = None
    volume: Optional[str] = None
    page: Optional[str] = None

    # timestamps
    created: datetime
    indexed: datetime
    posted: Optional[datetime] = None
    published: datetime
    deposited: datetime
    issued: Optional[datetime] = None
    accepted: Optional[datetime] = None
    content_created: Optional[datetime] = None
    content_updated: Optional[datetime] = None
    published_print: Optional[datetime] = None
    published_online: Optional[datetime] = None

    # "metadata"
    group_title: Optional[str] = None
    reference_count: Optional[int] = None
    references_count: Optional[int] = None
    subject: Optional[str] = None

    # Links
    #link: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None

    ## Additional props not in crossref
    unpaywall: Optional[str] = None
    scihub: Optional[str] = None




class Paper(PaperBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doi: str = Field(index=True, unique=True )
    journal: 'Journal' = Relationship(back_populates='papers')
    journal_id: Optional[int] = Field(default=None, foreign_key='journal.id')

    # TODO: handle updates
    # update-to: Optional['Paper']

class PaperRead(PaperBase):
    pass

class PaperCreate(PaperBase):
    pass