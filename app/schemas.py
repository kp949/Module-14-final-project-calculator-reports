"""Pydantic validation schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.calculation_factory import CalculationType


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    message: str
    user: UserRead


class AuthRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str | None = Field(default=None, min_length=3, max_length=50)


class AuthLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class CalculationRequest(BaseModel):
    a: float
    b: float


class CalculationCreate(BaseModel):
    a: float
    b: float
    type: CalculationType
    user_id: int | None = None

    @model_validator(mode="after")
    def validate_division(self):
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: CalculationType
    result: float
    user_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class ReportSummary(BaseModel):
    total_calculations: int 
    add_count: int
    subtract_count: int
    multiply_count: int
    divide_count: int
    average_result: float | None 
    highest_result: float | None
    lowest_result: float | None
    recent_calculations: list[CalculationRead]