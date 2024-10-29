from io import BytesIO
from typing import List
from functools import partial
from datetime import datetime
from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy import and_, desc, asc
from cachetools import TTLCache, cached
from sqlalchemy.ext.asyncio import AsyncSession


from src.api.settings import DAILY_LIKE_LIMIT
from src.api.models import Client, Match
from src.api.schemas import ClientSchema, CreateClientSchema
from src.api.utils import save_client_photo, calculate_distance, send_mutual_match_email, get_cache_key, decode_jwt


client_cache = TTLCache(maxsize=100, ttl=60)


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


@cached(cache=client_cache, key=partial(get_cache_key))
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


async def check_mutual_match(session: AsyncSession, target_client: Client, current_user: CreateClientSchema) -> bool:
    mutual_match = await session.execute(
        select(Match).where(
            Match.user_id == target_client.id,
            Match.target_user_id == current_user.id
        )
    )
    mutual_match = mutual_match.scalars().first()

    if mutual_match:
        return True
    return False


async def create_match_db(
        id: int,
        current_user: CreateClientSchema | None,
        session: AsyncSession) -> dict:

    if current_user.id == id:
        raise HTTPException(status_code=403, detail="You can't evaluate yourself!")

    target_client = await session.get(Client, id)

    if not target_client:
        raise HTTPException(status_code=404, detail="The client you want to send sympathy to is not there!")

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_likes_count = await session.execute(select(Match).where(
            Match.user_id == current_user.id,
            Match.time_created >= today_start
        )
    )

    if daily_likes_count.scalars().count() >= DAILY_LIKE_LIMIT:
        raise HTTPException(status_code=400, detail="Daily like limit reached.")

    match = await session.execute(select(Match).where(
            Match.user_id == current_user.id,
            Match.target_user_id == target_client.id
        )
    )
    match = match.scalars().first()

    if not match:
        match = Match(user_id=current_user.id, target_user_id=target_client.id)
        session.add(match)
    else:
        raise HTTPException(status_code=400, detail="You have already matched this client.")

    await session.commit()

    mutual_match = await check_mutual_match(session, target_client, current_user)

    if mutual_match:
        result = await send_mutual_match_email(current_user, target_client)
        return result

    return {'message': 'Match sent!'}


async def get_current_user(request: Request, session: AsyncSession) -> CreateClientSchema | None:
    auth_token = request.cookies.get("auth_token")

    if not auth_token:
        return None

    current_user = await get_clients_db(
        session,
        None,
        None,
        email=decode_jwt(auth_token)['email'])

    return current_user
