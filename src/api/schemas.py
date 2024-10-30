from typing import Literal
from pydantic import EmailStr, BaseModel


class ClientSchema(BaseModel):

    id: int | None
    email: EmailStr
    first_name: str | None
    last_name: str | None
    gender: Literal["male", "female"]
    photo: str | None
    longitude: float | None
    latitude: float | None

    class Config:
        orm_mode = True
        from_attributes = True


class CreateClientSchema(ClientSchema):

    password: str


class LoginClientSchema(BaseModel):

    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        from_attributes = True


class AuthTokenSchema(BaseModel):

    auth_token: str

    class Config:
        orm_mode = True
        from_attributes = True
