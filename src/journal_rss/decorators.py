"""
Decorators! What else u want me 2 say about em

Uses [PEP 612](https://peps.python.org/pep-0612/) annotations for
function decorations
"""
from typing import Callable, ParamSpec, TypeVar

Param = ParamSpec("Param")
ReturnType = TypeVar("ReturnType")
OriginalFunc = Callable[Param, ReturnType]


def singleton(func: OriginalFunc) -> OriginalFunc:
    """
    Wraps a function, returning the return value from the first time
    it is called.

    Todo:
        Currently doesn't check for reinstantiation using different parameters,
        so the singleton is 'sticky' throughout an interpreter session.

    References:
        - https://stackabuse.com/creating-a-singleton-in-python/
    """
    instances = {}

    def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> ReturnType:
        if not hasattr(wrapper, '_instance'):
            res = func(*args, **kwargs)
            wrapper._instance = res
        return wrapper._instance

    return wrapper
