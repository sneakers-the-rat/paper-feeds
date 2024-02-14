from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from paper_feeds.models import Paper


class JournalBase(SQLModel):
    title: str
    publisher: str
    homepage_url: str | None = None
    recent_paper_count: int
    feed: bool = False
    feed_created: datetime | None = None


class Journal(JournalBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    issn: list["ISSN"] = Relationship(back_populates="journal")
    papers: list["Paper"] = Relationship(back_populates="journal")


class JournalCreate(JournalBase):
    issn: list["ISSNCreate"]

    @classmethod
    def from_crossref(cls, res: dict) -> "JournalCreate":
        """
        See https://api.crossref.org/swagger-ui/index.html#/Journals/get_journals
        """
        # if issns match, prune duplicates
        if len(res["ISSN"]) > 1 and any([i == res["ISSN"][0] for i in res["ISSN"][1:]]):
            issns = [res["issn-type"][0]]
        else:
            issns = res["issn-type"]

        return JournalCreate(
            title=res["title"],
            publisher=res["publisher"],
            issn=issns,
            recent_paper_count=res["counts"]["current-dois"],
        )


class JournalRead(JournalBase):
    id: int
    issn: list["ISSN"]
    # feed: Optional['Feed'] = None


# --------------------------------------------------


class ISSNBase(SQLModel):
    type: str
    value: str = Field(unique=True)


class ISSN(ISSNBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    journal: Journal = Relationship(back_populates="issn")
    journal_id: int | None = Field(default=None, foreign_key="journal.id")


class ISSNRead(ISSNBase):
    id: int


class ISSNCreate(ISSNBase):
    pass
