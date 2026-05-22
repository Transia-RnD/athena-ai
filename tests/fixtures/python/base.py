"""Base class for testing Python indexing."""


class BaseClass:
    """Base class with methods to test indexing."""

    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        """Get the name of the object."""
        return self.name

    def print_info(self) -> None:
        """Print information about the object."""
        print(f"BaseClass: {self.name}")

    def calculate(self, x: int, y: int) -> int:
        """Calculate sum of two numbers."""
        return x + y


def helper_function(value: int) -> int:
    """Helper function that doubles a value."""
    return value * 2
