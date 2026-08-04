import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app import crud, models
from app.calculation_factory import CalculationType
from app.database import Base
from app.schemas import CalculationCreate, UserCreate


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_calculations.db")

connect_args = {}
if TEST_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_calculation_stores_correct_data(db_session):
    calculation = CalculationCreate(a=2, b=3, type=CalculationType.ADD)

    saved = crud.create_calculation(db_session, calculation)

    assert saved.id is not None
    assert saved.a == 2
    assert saved.b == 3
    assert saved.type == "Add"
    assert saved.result == 5


def test_create_calculation_with_user_foreign_key(db_session):
    user = crud.create_user(
        db_session,
        UserCreate(
            username="alice",
            email="alice@example.com",
            password="Password123",
        ),
    )
    calculation = CalculationCreate(
        a=20,
        b=4,
        type=CalculationType.DIVIDE,
        user_id=user.id,
    )

    saved = crud.create_calculation(db_session, calculation)

    assert saved.user_id == user.id
    assert saved.result == 5


def test_get_calculation_by_id(db_session):
    saved = crud.create_calculation(
        db_session,
        CalculationCreate(a=4, b=5, type=CalculationType.MULTIPLY),
    )

    found = crud.get_calculation_by_id(db_session, saved.id)

    assert found.id == saved.id
    assert found.result == 20


def test_calculation_model_requires_result(db_session):
    db_session.add(models.Calculation(a=1, b=2, type="Add", result=None))

    with pytest.raises(IntegrityError):
        db_session.commit()
