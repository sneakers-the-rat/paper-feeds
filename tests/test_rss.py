import pytest

from journal_rss.models.rss import PaperRSSFeed

@pytest.mark.parametrize(
    ('issn'),
    (
        '0896-6273',  # Neuron
    )
)
def test_paper_feed(issn):
    # TODO: Make this an actual test with a fixture that populates the database first

    feed = PaperRSSFeed.from_issn(issn)