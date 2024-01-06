import pdb

# need to set locale if unset to avoid https://github.com/sbordeyne/fastapi_rss/issues/8
import locale
import os
if locale.getlocale()[0] is None:
    os.environ['LC_ALL'] = 'en_US'

from fastapi_rss import RSSFeed, Item
from sqlmodel import Session, select
from sqlalchemy import desc

from paper_feeds.models import Journal, ISSN, Paper
from paper_feeds.db import get_engine
from paper_feeds.services.crossref import load_journal
from paper_feeds import Config

class PaperItem(Item):
    @classmethod
    def from_db(cls, paper: Paper) -> 'PaperItem':
        return PaperItem(
            title=paper.title,
            link=paper.url,
            description=paper.abstract,
            author=paper.author,
            pub_date=paper.created,
            category = None,
            comments = None,
            enclosure = None,
            guid = None,
            source = None,
            itunes = None
        )



class PaperRSSFeed(RSSFeed):

    @classmethod
    def _make_items(cls, papers: list[Paper]) -> list[PaperItem]:
        res = []
        for paper in papers:
            res.append(PaperItem.from_db(paper))
        return res

    @classmethod
    def from_issn(cls, issn:str, limit:int=500):
        engine = get_engine()
        with Session(engine) as session:
            # get journal
            journal = load_journal(issn)
            # get papers
            paper_statement = select(Paper).join(Journal
                 ).where(Paper.journal_id == journal.id
                 ).order_by(desc(Paper.created)
                 ).limit(limit)
            papers = session.exec(paper_statement).all()

        items = cls._make_items(papers)

        return PaperRSSFeed(
            title=journal.title,
            link = Config().public_url + f'/journals/{issn}/rss',
            description="Fill this in later lmao",
            item=items,
            copyright = None,
            managing_editor = None,
            webmaster = None,
            pub_date = None,
            last_build_date = None,
            category = None,
            cloud = None,
            image = None,
            text_input = None,
        )


