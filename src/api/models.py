from sqlalchemy import String, Float, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, relationship

from src.api.database import BaseModel


class Client(BaseModel):

    first_name = mapped_column(String(length=64), nullable=True)
    last_name = mapped_column(String(length=64), nullable=True)
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

    given_matches = relationship("Match", foreign_keys="[Match.user_id]", back_populates="user")
    received_matches = relationship("Match", foreign_keys="[Match.target_user_id]", back_populates="target_user")


class Match(BaseModel):

    user_id = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    target_user_id = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "target_user_id", name="unique_match"),)

    user = relationship("Client", foreign_keys=[user_id], back_populates="given_matches")
    target_user = relationship("Client", foreign_keys=[target_user_id], back_populates="received_matches")
