from sqlalchemy import String, Float
from sqlalchemy.orm import mapped_column

from src.api.database import BaseModel


class Client(BaseModel):

    first_name = mapped_column(String(length=64), nullable=True)
    second_name = mapped_column(String(length=64), nullable=True)
    email = mapped_column(String(length=64), nullable=False, unique=True)
    gender = mapped_column(String(length=10), nullable=True, default="не выбрано")
    photo = mapped_column(String(length=256), nullable=True)

    """
        Фото пользователя будет хранится в отдельной папке в приложении.
        В самой базе данных будет находится только путь до фото пользователя.
    """

    password = mapped_column(String(length=256), nullable=False)
    longitude = mapped_column(Float, nullable=True)
    latitude = mapped_column(Float, nullable=True)

