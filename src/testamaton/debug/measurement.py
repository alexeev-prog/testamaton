from functools import wraps
from time import time
from typing import Callable, Awaitable, Any

from rich import print


def async_debug_measurement(label: str = "measurement") -> Awaitable:
    def decorator(func: Awaitable) -> Awaitable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start = time()
            result = await func(*args, **kwargs)
            end = time()

            total = round(end - start, 9)

            print(
                "[bold dim]{}[/bold dim] : {}".format(
                    f"{func.__name__} | {label}".ljust(len(label) * 2), total
                )
            )

            return result


def debug_measurement(label: str = "measurement") -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time()
            result = func(*args, **kwargs)
            end = time()

            total = round(end - start, 9)

            print(
                "[bold dim]{}[/bold dim] : {}".format(
                    f"{func.__name__} | {label}".ljust(len(label) * 2), total
                )
            )

            return result

        return wrapper

    return decorator
