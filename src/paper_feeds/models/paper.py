from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from paper_feeds.models import Journal

from paper_feeds.const import SCIHUB_URL


class PaperBase(SQLModel):
    """https://api.crossref.org/swagger-ui/index.html#model-Work"""

    doi: str
    title: str
    subtitle: str | None = None
    short_title: str | None = None
    author: str
    type: str
    abstract: str | None = None

    # indexing
    publisher: str
    edition_number: str | None = None
    issue: str | None = None
    volume: str | None = None
    page: str | None = None

    # timestamps
    created: datetime
    indexed: datetime
    posted: datetime | None = None
    published: datetime
    deposited: datetime
    issued: datetime | None = None
    accepted: datetime | None = None
    content_created: datetime | None = None
    content_updated: datetime | None = None
    published_print: datetime | None = None
    published_online: datetime | None = None

    # "metadata"
    group_title: str | None = None
    reference_count: int | None = None
    references_count: int | None = None
    subject: str | None = None

    # Links
    # link: Optional[str] = None
    url: str | None = None
    source: str | None = None

    ## Additional props not in crossref
    unpaywall: str | None = None
    scihub: str | None = None


class Paper(PaperBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    doi: str = Field(index=True, unique=True)
    journal: "Journal" = Relationship(back_populates="papers")
    journal_id: int | None = Field(default=None, foreign_key="journal.id")

    # TODO: handle updates
    # update-to: Optional['Paper']


class PaperRead(PaperBase):
    pass


class PaperCreate(PaperBase):

    @classmethod
    def from_crossref(cls, res: dict) -> "PaperCreate":
        """
        Create a Paper from crossref metadata.

        References:
            - https://api.crossref.org/swagger-ui/index.html#model-Work
        """
        return PaperCreate(
            doi=res["DOI"],
            url=res["URL"],
            abstract=res.get("abstract", ""),
            author=_simplify_author(res.get("author", [])),
            created=_simplify_datetime(res["created"]),
            deposited=_simplify_datetime(res["deposited"]),
            edition_number=res.get("edition-number"),
            indexed=_simplify_datetime(res["indexed"]),
            issue=res.get("issue"),
            issued=_simplify_datetime(res.get("issued")),
            page=res.get("page"),
            posted=_simplify_datetime(res.get("posted")),
            published=_simplify_datetime(res.get("published")),
            published_print=_simplify_datetime(res.get("published-print")),
            published_online=_simplify_datetime(res.get("published-online")),
            publisher=res["publisher"],
            reference_count=res.get("reference-count"),
            references_count=res.get("references-count"),
            short_title=res.get("short-title"),
            source=res.get("source"),
            subject=", ".join(res.get("subject", [""])),
            title=_unwrap_list(res.get("title", [])),
            type=res["type"],
            volume=res.get("volume"),
            scihub=SCIHUB_URL + res["DOI"],
        )


def _simplify_author(author: list[dict]) -> str:
    """
    'author': [{'affiliation': [],
         'family': 'FirstName',
         'given': 'LastName',
         'sequence': 'first'}],
    """
    names = []
    for name in author:
        if name.get("name", None):
            names.append(name.get("name"))
            continue

        # don't use get bc want to fail to find out what possible values are
        if name["sequence"] in ("first", "additional"):
            name_parts = []
            if name.get("given", None):
                name_parts.append(name["given"])
            if name.get("family", None):
                name_parts.append(name["family"])

            names.append(" ".join(name_parts))
        else:
            raise ValueError(f'unhandled name sequence {name["sequence"]}')

    return ", ".join(names)


def _simplify_datetime(date: dict) -> datetime | None:
    """
    date = {
        'date-parts': [[2023, 12, 21]],
        'date-time': '2023-12-21T00:07:03Z',
        'timestamp': 1703117223000},
    }

    :param date:
    :return:
    """
    if date is None:
        return None

    if date.get("timestamp"):
        timestamp = float(date.get("timestamp"))
        if timestamp > 1_000_000_000_000:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp, tz=UTC)
    elif date.get("date-time"):
        return datetime.fromisoformat(date.get("date-time"))
    elif date.get("date-parts"):
        parts = date.get("date-parts")
        if isinstance(parts[0], list):
            parts = parts[0]

        if parts[0] is None:
            # eg. "issued" on http://api.crossref.org/journals/1674-9251/works?rows=1&offset=566&sort=published&order=desc
            return None

        if len(parts) == 1:
            # add the first month of the year
            parts.append(1)

        if len(parts) == 2:
            # add the first day of the month
            parts.append(1)
        return datetime(*parts, tzinfo=UTC)
    else:
        raise ValueError(f"Cant handle date: {date}")


def _unwrap_list(input: list | str, sep: str = ", ") -> str | None:
    if isinstance(input, str):
        return input
    elif input is None:
        return None
    else:
        return sep.join(input)
