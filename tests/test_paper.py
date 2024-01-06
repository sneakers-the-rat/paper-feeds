import pytest
from datetime import datetime, timezone

from paper_feeds.models.paper import _simplify_datetime

@pytest.mark.parametrize(
    'test,expected',
    [
        # humongous unix timestamps
        ({'timestamp':1704356642147.0488}, datetime(2024, 1, 4, 8, 24, 2, 147049, tzinfo=timezone.utc)),
        # regular unix timestamp
        ({'timestamp':1704356730.163272}, datetime(2024, 1, 4, 8, 25, 30, 163272, tzinfo=timezone.utc)),
        # timestamp as string
        ({'timestamp':'1704356730.163272'}, datetime(2024, 1, 4, 8, 25, 30, 163272, tzinfo=timezone.utc)),
        # isoformat timestamp
        ({'date-time': '2024-01-04T00:28:22Z'}, datetime(2024, 1, 4, 0, 28, 22, tzinfo=timezone.utc)),
        # regular date parts
        ({'date-parts': [[2024,1,1]]}, datetime(2024,1,1, tzinfo=timezone.utc)),
        # truncated date parts
        ({'date-parts': [[2024,1]]}, datetime(2024,1,1, tzinfo=timezone.utc)),
        ({'date-parts': [[2024]]}, datetime(2024,1,1, tzinfo=timezone.utc)),
        # https://github.com/sneakers-the-rat/paper-feeds/issues/16
        ({'date-parts': [[None]]}, None)
    ]
)
def test_simplify_datetime(test, expected):
    assert _simplify_datetime(test) == expected