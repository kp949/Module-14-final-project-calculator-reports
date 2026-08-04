"""Database actions for users and calculations."""

from sqlalchemy.orm import Session

from app import models
from app.calculation_factory import calculate_result
from app.schemas import CalculationCreate, UserCreate
from app.security import hash_password


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_calculation_by_id(db: Session, calculation_id: int):
    return db.query(models.Calculation).filter(models.Calculation.id == calculation_id).first()


def get_user_calculation_by_id(db: Session, calculation_id: int, user_id: int):
    return (
        db.query(models.Calculation)
        .filter(models.Calculation.id == calculation_id, models.Calculation.user_id == user_id)
        .first()
    )


def get_calculations(db: Session):
    return db.query(models.Calculation).order_by(models.Calculation.id).all()


def get_calculations_for_user(db: Session, user_id: int):
    return (
        db.query(models.Calculation)
        .filter(models.Calculation.user_id == user_id)
        .order_by(models.Calculation.id)
        .all()
    )


def create_calculation(db: Session, calculation: CalculationCreate):
    result = calculate_result(calculation.a, calculation.b, calculation.type)
    db_calculation = models.Calculation(
        a=calculation.a,
        b=calculation.b,
        type=calculation.type.value,
        result=result,
        user_id=calculation.user_id,
    )
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def update_calculation(db: Session, db_calculation: models.Calculation, calculation: CalculationCreate):
    db_calculation.a = calculation.a
    db_calculation.b = calculation.b
    db_calculation.type = calculation.type.value
    db_calculation.result = calculate_result(calculation.a, calculation.b, calculation.type)
    db_calculation.user_id = calculation.user_id
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def delete_calculation(db: Session, db_calculation: models.Calculation):
    db.delete(db_calculation)
    db.commit()
