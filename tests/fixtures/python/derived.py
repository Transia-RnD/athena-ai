"""Derived class inheriting from BaseClass."""

from base import BaseClass


class DerivedClass(BaseClass):
    """Derived class that extends BaseClass."""

    def __init__(self, name: str, id: int):
        super().__init__(name)
        self.id = id

    def get_name(self) -> str:
        """Override get_name to include ID."""
        return f"{self.name} (ID: {self.id})"

    def get_id(self) -> int:
        """Get the ID of the object."""
        return self.id

    def process_data(self, a: int, b: int) -> int:
        """Process data using parent's calculate method."""
        result = self.calculate(a, b)
        return result * self.id
