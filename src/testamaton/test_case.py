from functools import partial, wraps
from logging import Logger, getLogger
from time import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

from testamaton.exceptions import TestError
from testamaton.reporter import print_header, print_results_table
from testamaton.sessions import Runner
from testamaton.standard import (
    Argument,
    CollectionMetadata,
    Each,
    ExpectFailMarkup,
    Fixture,
    SkipMarker,
)

__tlogger: Logger = getLogger(__name__)


def skip(
    func_or_reason: Union[str, Callable, None] = None,
    *,
    reason: Optional[str] = None,
    when: Union[bool, Callable] = True,
) -> Callable:
    if func_or_reason is None:
        return partial(skip, reason=reason, when=when)

    if isinstance(func_or_reason, str):
        return partial(skip, reason=func_or_reason, when=when)

    func: Union[str, Callable, None] = func_or_reason

    marker = SkipMarker(reason=reason, when=when)

    if hasattr(func, "ward_meta"):
        func.__testamatonmeta.marker = marker
    else:
        func.__testamatonmeta = CollectionMetadata(marker=marker)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def expectfail(
    func_or_reason: Union[str, Callable, None] = None,
    *,
    reason: Optional[str] = None,
    when: Union[bool, Callable] = True,
) -> Callable:
    if func_or_reason is None:
        return partial(expectfail, reason=reason, when=when)

    if isinstance(func_or_reason, str):
        return partial(expectfail, reason=func_or_reason, when=when)

    func: Union[str, Callable, None] = func_or_reason
    marker = ExpectFailMarkup(reason=reason, when=when)

    if hasattr(func, "__testamatonmeta"):
        func.__testamatonmeta.marker = marker
    else:
        func.__testamatonmeta = CollectionMetadata(marker=marker)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class BaseTestCase:
    def __init__(self, label: str = "TestCase") -> None:
        self.label: str = label

        self.warnings: int = 0
        self.tags: List[str] = []
        self.fixtures: Dict[str, Fixture] = []
        self.skipped: int = 0
        self.errors: int = 0
        self.passed: int = 0

        self.tests: Dict[str, Union[Callable, Awaitable]] = {}


class TestCase(BaseTestCase):
    def __init__(self, label: str = "TestCase") -> None:
        super().__init__(label)

    def fixture(self) -> Callable:
        def wrapper(
            func: Union[Awaitable, Callable], *args, **kwargs
        ) -> Union[Awaitable, Callable]:
            if not hasattr(func, "__testamatonmeta"):
                func.__testamatonmeta = CollectionMetadata(is_fixture=True)
            else:
                func.__testamatonmeta.is_fixture = True

            self.fixtures[func.__name__] = Fixture(handler=func)

            __tlogger.warning("Fixtures not fully implemented")

            return func(*args, **kwargs)

        return wrapper

    def test(
        self,
        comment: str = None,
        tags: List[str] = [],
        count_of_launchs: int = 1,
        arguments: Tuple[Argument] = (),
    ) -> Callable:
        def wrapper(
            func: Union[Awaitable, Callable], *args, **kwargs
        ) -> Union[Awaitable, Callable]:
            if not hasattr(func, "__testamatonmeta"):
                func.__testamatonmeta = CollectionMetadata(
                    comment=comment.format(**kwargs) if comment is not None else None,
                    tags=tags,
                    arguments=arguments,
                    count_of_launchs=count_of_launchs,
                )
            else:
                func.__testamatonmeta.comment = (
                    comment.format(**kwargs) if comment is not None else None
                )
                func.__testamatonmeta.tags = tags
                func.__testamatonmeta.arguments = arguments
                func.__testamatonmeta.count_of_launchs = count_of_launchs

            self.tags = list(set(self.tags + tags))

            self.tests[func.__name__] = func
            return func

        return wrapper

    def run(self, tags: Optional[List[str]] = []) -> None:
        runner = Runner(self.tests, self)

        start: float = time()

        runner.launch_test_chain(tags=tags)

        end: float = time()
        total: float = end - start

        print_header(
            f"[cyan]{len(self.tests)} tests runned {round(total, 2)}s[/cyan]",
            plus_len=15,
        )

        print_results_table(
            len(self.tests), self.passed, self.warnings, self.errors, self.skipped
        )


def expect(lhs: Any, rhs: Any, message: str) -> bool:
    if lhs == rhs:
        return True
    else:
        raise TestError(message)


def each(*args) -> Each:
    return Each(args)
