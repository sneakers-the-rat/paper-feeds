from paper_feeds.config import config
from paper_feeds.db import get_engine
from paper_feeds.models.journal import Journal, ISSN
from paper_feeds.services import openalex
from sqlmodel import Session, select


def get_journals_homepage(journals: list[Journal]):
    # extract one issn of each journal newly added to DB
    issns_to_query = []
    for journal in journals:
        if journal.issn:
            issns_to_query += [journal.issn[0].value]

    # call OpenAlex to get a mapping: ISSN -> homepage URL
    issn_hp_map = openalex.get_journal_homepages(issns_to_query)

    # filter incoming issns: only keep the ones where homepage URL has value
    issns_to_update = [issn for issn in issns_to_query if issn_hp_map[issn]]
    issn_hp_map_to_update = {issn: issn_hp_map[issn] for issn in
                             issns_to_update}

    # store homepage_urls in DB
    update_journals_homepage_urls(issn_hp_map_to_update)


def update_journals_homepage_urls(issn_hp_map: dict) -> None:
    """
    Update homepage_url for multiple Journals
    based on mapping: issn -> homepage_url.
    """
    engine = get_engine(config)
    with Session(engine) as session:

        for issn, homepage_url in issn_hp_map.items():
            # fetch Journal by ISSN
            statement = select(Journal).join(ISSN).where(ISSN.value == issn)
            journal = session.exec(statement).one()

            # update homepage_url
            if journal:
                journal.homepage_url = homepage_url
                session.add(journal)
                session.commit()
                session.refresh(journal)
