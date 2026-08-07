"""Module 14 FastAPI JWT application with calculation BREAD routes."""

import logging

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import crud
from app.database import Base, engine, get_db
from app.models import User
from app.operations import add, divide, multiply, subtract
from app.schemas import (
    AuthLogin,
    AuthRegister,
    CalculationCreate,
    CalculationRead,
    CalculationRequest,
    LoginResponse,
    MessageResponse,
    UserCreate,
    UserLogin,
    UserRead,
    TokenResponse,
    ReportSummary,
)
from app.security import create_access_token, decode_access_token, verify_password


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Module 14 Calculation BREAD Application")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Module 14 Calculation BREAD Application</title></head>
        <body>
            <h1>Module 14 Calculation BREAD Application</h1>
            <p>The API is running. Try /docs, /static/register.html, /static/login.html, or /static/calculations.html.</p>
        </body>
    </html>
    """


@app.get("/health")
def health_check():
    return {"status": "ok"}


def _register_user(user: UserCreate, db: Session):
    if crud.get_user_by_username(db, user.username):
        logger.warning("Duplicate username attempted: %s", user.username)
        raise HTTPException(status_code=400, detail="Username already exists")

    if crud.get_user_by_email(db, user.email):
        logger.warning("Duplicate email attempted: %s", user.email)
        raise HTTPException(status_code=400, detail="Email already exists")

    logger.info("Creating user: %s", user.username)
    return crud.create_user(db, user)


def _username_from_email(email: str) -> str:
    username = email.split("@", 1)[0].replace(".", "_").replace("-", "_")
    return username[:50] if len(username) >= 3 else "user"


def _token_for_user(user) -> str:
    return create_access_token({"sub": user.email, "user_id": user.id})


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=401, detail="Invalid authorization token") from error

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authorization token")

    user = crud.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return _register_user(user, db)


@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return _register_user(user, db)


@app.post("/users/login", response_model=LoginResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user is None or not verify_password(user.password, db_user.password_hash):
        logger.warning("Failed login attempt for username: %s", user.username)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    logger.info("User logged in: %s", user.username)
    return {"message": "Login successful", "user": db_user}


@app.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def jwt_register_user(user: AuthRegister, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        logger.warning("Duplicate JWT registration email attempted: %s", user.email)
        raise HTTPException(status_code=400, detail="Email already exists")

    username = user.username or _username_from_email(user.email)
    new_user = UserCreate(username=username, email=user.email, password=user.password)
    db_user = _register_user(new_user, db)
    token = _token_for_user(db_user)
    return {
        "message": "Registration successful",
        "access_token": token,
        "token_type": "bearer",
        "user": db_user,
    }


@app.post("/login", response_model=TokenResponse)
def jwt_login_user(user: AuthLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user is None or not verify_password(user.password, db_user.password_hash):
        logger.warning("Failed JWT login attempt for email: %s", user.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _token_for_user(db_user)
    logger.info("JWT login successful for email: %s", user.email)
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": db_user,
    }


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _validate_calculation_user(calculation: CalculationCreate, db: Session):
    if calculation.user_id is not None and crud.get_user_by_id(db, calculation.user_id) is None:
        raise HTTPException(status_code=400, detail="User does not exist")


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_calculations_for_user(db, current_user.id)


@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(
    calculation: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calculation.user_id = current_user.id
    return crud.create_calculation(db, calculation)


@app.get("/calculations/{calculation_id}", response_model=CalculationRead)
def read_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calculation = crud.get_user_calculation_by_id(db, calculation_id, current_user.id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.put("/calculations/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int,
    calculation: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_calculation = crud.get_user_calculation_by_id(db, calculation_id, current_user.id)
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")

    calculation.user_id = current_user.id
    return crud.update_calculation(db, db_calculation, calculation)


@app.delete("/calculations/{calculation_id}", response_model=MessageResponse)
def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calculation = crud.get_user_calculation_by_id(db, calculation_id, current_user.id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")

    crud.delete_calculation(db, calculation)
    return {"message": "Calculation deleted"}


@app.get("/reports/summary", response_model=ReportSummary)
def calculation_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calculations = crud.get_calculations_for_user(db, current_user.id)
    results = [calculation.result for calculation in calculations]

    return {
        "total_calculations": len(calculations),
        "add_count": sum(1 for calculation in calculations if calculation.type == "Add"),
        "subtract_count": sum(1 for calculation in calculations if calculation.type == "Sub"),
        "multiply_count": sum(1 for calculation in calculations if calculation.type == "Multiply"),
        "divide_count": sum(1 for calculation in calculations if calculation.type == "Divide"),
        "average_result": sum(results) / len(results) if results else None,
        "highest_result": max(results) if results else None,
        "lowest_result": min(results) if results else None,
        "recent_calculations": calculations[-5:],
    }

@app.post("/add")
def add_numbers(request: CalculationRequest):
    return {"result": add(request.a, request.b)}


@app.post("/subtract")
def subtract_numbers(request: CalculationRequest):
    return {"result": subtract(request.a, request.b)}


@app.post("/multiply")
def multiply_numbers(request: CalculationRequest):
    return {"result": multiply(request.a, request.b)}


@app.post("/divide")
def divide_numbers(request: CalculationRequest):
    try:
        result = divide(request.a, request.b)
    except ValueError as error:
        logger.error("Division error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"result": result}
