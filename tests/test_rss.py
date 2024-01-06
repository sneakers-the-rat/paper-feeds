import pytest

from paper_feeds.models.rss import PaperRSSFeed
from .fixtures import base_data

@pytest.mark.parametrize(
    ('issn'),
    (
        '0896-6273',  # Neuron
    )
)
def test_paper_feed(issn, base_data):
    # TODO: Make this an actual test with a fixture that populates the database first

    feed = PaperRSSFeed.from_issn(issn)