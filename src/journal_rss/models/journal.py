from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
if TYPE_CHECKING:
    from journal_rss.models import Feed

class JournalBase(SQLModel):
    title: str
    publisher: str
    feed_created: Optional[datetime] = None

class Journal(JournalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    issn: List['ISSN'] = Relationship(back_populates='journal')
    # feed: Optional['Feed'] = Relationship(back_populates='journal')


class JournalCreate(JournalBase):
    issn: list['ISSNCreate']

    @classmethod
    def from_crossref(cls, res:dict):
        """
        See https://api.crossref.org/swagger-ui/index.html#/Journals/get_journals
        """
        return JournalCreate(
            title=res['title'],
            publisher=res['publisher'],
            issn = res['issn-type']
        )


class JournalRead(JournalBase):
    id: int
    issn: list['ISSN']
    # feed: Optional['Feed'] = None

# --------------------------------------------------

class ISSNBase(SQLModel):
    type: str
    value: str = Field(unique=True)


class ISSN(ISSNBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    journal: Journal = Relationship(back_populates='issn')
    journal_id: Optional[int] = Field(default=None, foreign_key='journal.id')

class ISSNRead(ISSNBase):
    id: int

class ISSNCreate(ISSNBase):
    pass
