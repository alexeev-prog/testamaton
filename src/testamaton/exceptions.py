class TestError(Exception):
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explaination(self) -> None:
        return f"Message: {self.message if self.message else 'missing'}"

    def __str__(self) -> str:
        return f"TestError has been raised. {self.get_explanation()}"


class SkippedTestException(TestError):
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = "SkippedTest"

    def __str__(self) -> str:
        return f"{self.message}"


class TestValidationError(TestError):
    def __str__(self) -> str:
        return f"TestValidationError has been raised. {self.get_explanation()}"


class FixtureError(TestError):
    def __str__(self) -> str:
        return f"FixtureError has been raised. {self.get_explanation()}"
