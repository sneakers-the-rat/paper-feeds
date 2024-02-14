from paper_feeds.decorators import singleton
from datetime import datetime
from time import sleep


def test_singleton():
    """
    Singletons should return the same result when called naively, but also create a
    function attribute so that singleton can be manually modified (eg. for testing)
    """

    @singleton
    def my_function() -> datetime:
        return datetime.now()

    @singleton
    def my_second_function() -> datetime:
        return datetime.now()

    first_call = my_function()
    # sleep super briefly to ensure different result if calling again
    sleep(0.005)
    second_call = my_function()
    assert first_call == second_call
    assert first_call is second_call

    # multiple singletons should not interfere with each other
    other_call = my_second_function()
    assert first_call != other_call
    assert first_call is not other_call

    # we should be able to override the singleton value explicitly
    sleep(0.005)
    new_time = datetime.now()
    assert new_time != second_call
    my_function._instance = new_time
    third_call = my_function()
    assert third_call == new_time
    assert third_call is new_time
