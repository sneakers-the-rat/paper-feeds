from typing import Optional, TYPE_CHECKING
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
if TYPE_CHECKING:
    from journal_rss.models import Journal, ISSN

class FeedBase(SQLModel):
    timestamp_start: datetime = Field(default_factory=datetime.now)

class Feed(FeedBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # issn: list['ISSN'] = Relationship(back_populates='feed')
    # journal_id: int = Field(default=None, foreign_key='feed.id')
    # journal: 'Journal' = Relationship(back_populates='feed')