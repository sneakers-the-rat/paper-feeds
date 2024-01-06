from typing import Optional, Union, Tuple, List, Dict, Literal, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
if TYPE_CHECKING:
    from paper_feeds.models import Journal

from paper_feeds.const import SCIHUB_URL



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

    @classmethod
    def from_crossref(cls, res: dict) -> 'PaperCreate':
        """
        Create a Paper from crossref metadata.

        References:
            - https://api.crossref.org/swagger-ui/index.html#model-Work
        """
        return PaperCreate(
            doi=res['DOI'],
            url=res['URL'],
            abstract = res.get('abstract', ''),
            author=_simplify_author(res.get('author', [])),
            created=_simplify_datetime(res['created']),
            deposited=_simplify_datetime(res['deposited']),
            edition_number=res.get('edition-number', None),
            indexed=_simplify_datetime(res['indexed']),
            issue=res.get('issue', None),
            issued=_simplify_datetime(res.get('issued', None)),
            page=res.get('page', None),
            posted=_simplify_datetime(res.get('posted', None)),
            published=_simplify_datetime(res.get('published', None)),
            published_print=_simplify_datetime(res.get('published-print', None)),
            published_online=_simplify_datetime(res.get('published-online', None)),
            publisher=res['publisher'],
            reference_count=res.get('reference-count', None),
            references_count=res.get('references-count', None),
            short_title=res.get('short-title', None),
            source=res.get('source', None),
            subject=', '.join(res.get('subject', [''])),
            title=_unwrap_list(res.get('title', [])),
            type=res['type'],
            volume=res.get('volume', None),
            scihub=SCIHUB_URL + res['DOI']
        )



def _simplify_author(author) -> str:
    """
    'author': [{'affiliation': [],
         'family': 'FirstName',
         'given': 'LastName',
         'sequence': 'first'}],
    """
    names = []
    for name in author:
        if name.get('name', None):
            names.append(name.get('name'))
            continue

        # don't use get bc want to fail to find out what possible values are
        if name['sequence'] in ('first', 'additional'):
            name_parts = []
            if name.get('given', None):
                name_parts.append(name['given'])
            if name.get('family', None):
                name_parts.append(name['family'])

            names.append(' '.join(name_parts))
        else:
            raise ValueError(f'unhandled name sequence {name["sequence"]}')

    return ', '.join(names)

def _simplify_datetime(date: dict) -> Optional[datetime]:
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

    if date.get('timestamp', None):
        timestamp = float(date.get('timestamp'))
        if timestamp > 1_000_000_000_000:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    elif date.get('date-time', None):
        return datetime.fromisoformat(date.get('date-time'))
    elif date.get('date-parts', None):
        parts = date.get('date-parts')
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
        return datetime(*parts, tzinfo=timezone.utc)
    else:
        raise ValueError(f"Cant handle date: {date}")

def _unwrap_list(input: list | str, sep=', ') -> Optional[str]:
    if isinstance(input, str):
        return input
    elif input is None:
        return None
    else:
        return sep.join(input)

