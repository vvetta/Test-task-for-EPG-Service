from typing import Literal
from pydantic import EmailStr, BaseModel


class ClientSchema(BaseModel):

    id: int | None
    email: EmailStr
    fio: str | None
    gender: Literal["male", "female"]
    photo: str | None
    longitude: float | None
    latitude: float | None


class CreateClientSchema(ClientSchema):

    password: str
