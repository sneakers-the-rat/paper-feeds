from typing import Optional

from sqlmodel import Session, select

from paper_feeds.models import Journal, ISSN


def get_journal_by_issn(db_session: Session, issn: str) -> Optional[Journal]:
    """
    Retrieve a journal by its ISSN.

    Args:
        db_session (Session): The database session.
        issn (str): The ISSN of the journal to retrieve.

    Returns:
        Journal or None: The journal object if found, or None if not found.
    """
    statement = select(Journal).join(ISSN).where(ISSN.value == issn)
    journal = db_session.exec(statement).one()
    return journal


def update_journal_homepages(db_session: Session, journal_updates: dict):
    """
    Update multiple journals' homepage URLs based on a dictionary of ISSN to homepage_url mappings.

    Args:
        db_session (Session): The database session.
        journal_updates (dict): A dictionary where keys are ISSN values and values are homepage URLs.

    Returns:
        None
    """
    for issn, homepage_url in journal_updates.items():
        journal = get_journal_by_issn(db_session, issn)

        if journal:
            journal.homepage_url = homepage_url

    db_session.commit()
