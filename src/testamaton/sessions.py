import asyncio
import inspect
import traceback
from typing import Any, Awaitable, Callable, List, Union

from testamaton.exceptions import SkippedTestException, TestError
from testamaton.reporter import (
    TestResult,
    print_header,
    print_platform,
    print_test_result,
)
from testamaton.standard import ExpectFailMarkup, SkipMarker


class Runner:
    def __init__(self, tests: int, testcase: object) -> None:
        self.tests = tests
        self.tests_count = len(self.tests)
        self.testcase = testcase

    def _print_prelude(self) -> None:
        print_header("runner session starts")
        print_platform(self.tests_count)

    def _run_testinfo(self, test: Union[Callable, Awaitable], *args, **kwargs) -> Any:
        if inspect.iscoroutinefunction(test):
            result = asyncio.run(test(*args, **kwargs))
        else:
            result = test(*args, **kwargs)

        return result

    def _run_test_cycle(self, test: Union[Awaitable, Callable]) -> Any:
        for n in range(test.__testamatonmeta.count_of_launchs):
            if test.__testamatonmeta.arguments:
                for argument in test.__testamatonmeta.arguments:
                    result = self._run_testinfo(test, *argument.args, **argument.kwargs)
            else:
                result = self._run_testinfo(test)

        return result

    def _check_warnings(
        self, result: Any, results: list, percent: int, test_name: str
    ) -> None:
        if len(results) > 0 and results[-1] == result and result is not None:
            print_test_result(
                TestResult(
                    percent=percent,
                    label=test_name,
                    status="warning",
                    output=f"Last result is equals current result ({results[-1]} == {result})",
                )
            )
            self.testcase.warnings += 1
            self.testcase.passed += 1

    def _processing_tests_execution(
        self,
        tags: List[str],
        test_num: int,
        test_name: str,
        test: Union[Awaitable, Callable],
    ) -> None:
        percent = int((test_num / self.tests_count) * 100)
        results: list[Any] = []

        lines: int = inspect.getsourcelines(test)[1]
        test_name = f"{test_name}:[line {lines}]"

        try:
            if tags and list(set(tags) & set(test.tags)):
                raise SkippedTestException()
            elif isinstance(test.__testamatonmeta.marker, SkipMarker):
                marker = test.__testamatonmeta.marker

                if marker.when:
                    raise SkippedTestException(
                        marker.reason if marker.reason else "SkippedTest"
                    )
            elif isinstance(test.__testamatonmeta.marker, ExpectFailMarkup):
                marker: ExpectFailMarkup = test.__testamatonmeta.marker

            result = self._run_test_cycle(test_name, test)

            self._check_warnings(result, results, percent, test_name)

            results.append(result)
        except SkippedTestException as ex:
            self.testcase.skipped += 1
            print_test_result(
                TestResult(
                    percent=percent,
                    label=test_name,
                    status="skip",
                    postmessage=str(ex),
                    comment=test.__testamatonmeta.comment,
                )
            )
        except (AssertionError, TestError):
            self.testcase.errors += 1

            if isinstance(marker, ExpectFailMarkup):
                print_test_result(
                    TestResult(
                        percent=percent,
                        label=test_name,
                        status="error",
                        output=traceback.format_exc(),
                        postmessage=marker.reason if marker.reason else "XFAIL",
                        comment=test.__testamatonmeta.comment,
                    )
                )
            else:
                print_test_result(
                    TestResult(
                        percent=percent,
                        label=test_name,
                        status="error",
                        output=traceback.format_exc(),
                        comment=test.__testamatonmeta.comment,
                    )
                )
        else:
            self.testcase.passed += 1

            print_test_result(percent, test_name, comment=test.__testamatonmeta.comment)

    def launch_test_chain(self, tags: List[str]) -> None:
        for test_num, (test_name, test) in enumerate(self.tests.items(), start=1):
            self._processing_tests_execution(tags, test_num, test_name, test)
