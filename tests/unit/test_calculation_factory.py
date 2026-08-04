import pytest

from app.calculation_factory import CalculationType, calculate_result


@pytest.mark.parametrize(
    "a,b,calculation_type,expected",
    [
        (2, 3, CalculationType.ADD, 5),
        (10, 4, CalculationType.SUBTRACT, 6),
        (4, 5, CalculationType.MULTIPLY, 20),
        (20, 4, CalculationType.DIVIDE, 5),
    ],
)
def test_calculation_factory_returns_correct_result(a, b, calculation_type, expected):
    assert calculate_result(a, b, calculation_type) == expected


def test_calculation_factory_rejects_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculate_result(10, 0, CalculationType.DIVIDE)
