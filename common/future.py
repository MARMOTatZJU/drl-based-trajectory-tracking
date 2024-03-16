"""Components ensuring compatibility"""
from typing import Callable


def override(func: Callable) -> Callable:
    """Try to import `typing.override` which is supported only for Python>=3.12

    Args:
        func: Function desired to be decorated by `typing.override`

    Returns:
        Callable: Decorated function if Python>=3.12. Undecorated function otherwise.
    """
    try:
        from typing import override
        return override(func)
    except:
        return func
