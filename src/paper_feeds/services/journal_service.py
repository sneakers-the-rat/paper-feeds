from sqlmodel import Session

from paper_feeds.db import get_engine
from paper_feeds.models.journal import Journal
from paper_feeds.repositories.journal_repository import update_journal_homepages
from paper_feeds.services import openalex


def get_journal_homepages(journals: list[Journal], email: str | None) -> None:
    """
    Retrieves homepage URLs for journals from OpenAlex API and stores them in the
    database.

    Args:
        journals (list[Journal]): A list of Journal objects for which homepage URLs
            need to be obtained.
        email (Optional[str]): An optional email address used to access OpenAlex`s
            polite pool.

    Returns:
        None
    """

    # extract one issn of each journal newly added to DB
    issns_to_query = []
    for journal in journals:
        if journal.issn:
            issns_to_query += [journal.issn[0].value]

    # call OpenAlex to get a mapping: ISSN -> homepage URL
    issn_hp_map = openalex.get_journal_homepages(issns_to_query, email)

    # filter incoming issns: only keep the ones where homepage URL has value
    issns_to_update = [issn for issn in issns_to_query if issn_hp_map[issn]]
    issn_hp_map_to_update = {issn: issn_hp_map[issn] for issn in issns_to_update}

    # store homepage_urls in DB
    engine = get_engine()
    with Session(engine) as session:
        update_journal_homepages(session, issn_hp_map_to_update)
