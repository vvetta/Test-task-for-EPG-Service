from io import BytesIO
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy import and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import Client
from src.api.utils import save_client_photo, calculate_distance
from src.api.schemas import ClientSchema, CreateClientSchema


async def create_client_db(
        session: AsyncSession,
        client: CreateClientSchema,
        photo: BytesIO) -> ClientSchema:
    client = Client(**client.model_dump())
    client.photo = await save_client_photo(photo, client.email)

    session.add(client)

    try:
        await session.commit()
        return ClientSchema.from_orm(client)
    except Exception as e:
        raise HTTPException(status_code=403, detail="An error occurred while creating a new user.")


async def get_clients_db(
        session: AsyncSession,
        sort_order: str | None,
        current_user: CreateClientSchema | None,
        **kwargs) -> List[ClientSchema] | CreateClientSchema:
    query = select(Client)

    filters = []
    if kwargs.get('email'):
        result = await session.execute(query.where(Client.email == kwargs['email']))
        client = result.fetchone()
        return CreateClientSchema.from_orm(client)

    if kwargs.get('gender'):
        filters.append(Client.gender == kwargs['gender'])
    if kwargs.get('first_name'):
        filters.append(Client.first_name.ilike(f"%{kwargs['first_name']}%"))
    if kwargs.get('last_name'):
        filters.append(Client.last_name.ilike(f"%{kwargs['last_name']}%"))
    if kwargs.get('time_created'):
        filters.append(Client.time_created == kwargs['time_created'])

    if filters:
        query = query.where(and_(*filters))

    if sort_order == "desc":
        query = query.order_by(desc(Client.time_created))
    if sort_order == "asc" or not sort_order:
        query = query.order_by(asc(Client.time_created))

    result = await session.execute(query)
    clients = result.scalars().all()

    if kwargs.get('distance'):
        if not current_user:
            raise HTTPException(status_code=401, detail="You are not authorized!")

        if current_user.latitude is None or current_user.longitude is None:
            raise HTTPException(status_code=400, detail="Current user location is not set.")

        clients_in_range = [
            ClientSchema.from_orm(client) for client in clients
            if client.latitude is not None and client.longitude is not None
               and calculate_distance(current_user.latitude, current_user.longitude, client.latitude,
                                      client.longitude) <= kwargs['distance']
        ]

        return clients_in_range

    return [ClientSchema.from_orm(client) for client in clients]
