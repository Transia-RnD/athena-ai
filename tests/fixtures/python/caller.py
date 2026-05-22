"""Caller module that uses BaseClass and DerivedClass."""

from base import BaseClass, helper_function
from derived import DerivedClass


def process_objects() -> None:
    """Main processing function that calls methods from base and derived."""
    base = BaseClass("BaseObject")
    derived = DerivedClass("DerivedObject", 42)

    # Call methods on base class
    base_name = base.get_name()
    base_result = base.calculate(10, 20)
    base.print_info()

    # Call methods on derived class
    derived_name = derived.get_name()
    derived_result = derived.process_data(5, 10)
    id_value = derived.get_id()

    # Call standalone helper
    helper_result = helper_function(base_result)

    print(f"Processed: {base_name}, {derived_name}")


def calculate_total(x: int, y: int) -> int:
    """Calculate total using DerivedClass."""
    obj = DerivedClass("Calculator", 1)
    return obj.process_data(x, y)
