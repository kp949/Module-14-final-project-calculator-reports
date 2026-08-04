"""Factory for calculation operations."""

from enum import Enum

from app.operations import add, divide, multiply, subtract


class CalculationType(str, Enum):
    ADD = "Add"
    SUBTRACT = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


def calculate_result(a: float, b: float, calculation_type: CalculationType) -> float:
    if calculation_type == CalculationType.ADD:
        return add(a, b)
    if calculation_type == CalculationType.SUBTRACT:
        return subtract(a, b)
    if calculation_type == CalculationType.MULTIPLY:
        return multiply(a, b)
    if calculation_type == CalculationType.DIVIDE:
        return divide(a, b)

    raise ValueError("Invalid calculation type")
