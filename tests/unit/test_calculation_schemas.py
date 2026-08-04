import pytest
from pydantic import ValidationError

from app.calculation_factory import CalculationType
from app.schemas import CalculationCreate


def test_calculation_create_accepts_valid_data():
    calculation = CalculationCreate(a=2, b=3, type=CalculationType.ADD)

    assert calculation.a == 2
    assert calculation.b == 3
    assert calculation.type == CalculationType.ADD


def test_calculation_create_accepts_type_string():
    calculation = CalculationCreate(a=4, b=5, type="Multiply")

    assert calculation.type == CalculationType.MULTIPLY


def test_calculation_create_rejects_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=2, b=3, type="Power")


def test_calculation_create_rejects_division_by_zero():
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationCreate(a=10, b=0, type=CalculationType.DIVIDE)
