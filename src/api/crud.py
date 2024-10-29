from io import BytesIO
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import Client
from src.api.utils import save_client_photo
from src.api.schemas import ClientSchema, CreateClientSchema


async def create_client_db(
        session: AsyncSession,
        client: CreateClientSchema,
        photo: BytesIO) -> ClientSchema:

    client = Client(**client.model_dump())
    client.photo = await save_client_photo(photo)

    session.add(client)

    try:
        await session.commit()
        return ClientSchema.from_orm(client)
    except Exception as e:
        raise HTTPException(status_code=403, detail="An error occurred while creating a new user.")
