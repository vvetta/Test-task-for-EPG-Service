from typing import Literal
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Form, File, UploadFile, Depends, Response, HTTPException, Request

from src.api.utils import hash_password, add_watermark, encode_jwt
from src.api.database import get_session
from src.api.crud import create_client_db, get_clients_db, create_match_db, get_current_user
from src.api.schemas import CreateClientSchema, ClientSchema, LoginClientSchema, AuthTokenSchema


router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/create", response_model=ClientSchema)
async def create_client(
        email: EmailStr = Form(...),
        password: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        longitude: float = Form(...),
        latitude: float = Form(...),
        gender: Literal['male', 'female'] = Form(...),
        photo: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)) -> ClientSchema:

    client = CreateClientSchema(
        email=email,
        password=hash_password(password),
        photo=None,
        id=None,
        first_name=first_name,
        last_name=last_name,
        longitude=longitude,
        latitude=latitude,
        gender=gender
    )

    photo_w_wm = await add_watermark(photo)

    client = await create_client_db(session, client, photo_w_wm)

    return client


@router.post("/login", response_model=AuthTokenSchema)
async def login(login_payload: LoginClientSchema,
                response: Response,
                session: AsyncSession = Depends(get_session)) -> AuthTokenSchema:
    """Эндпоинт авторизации клиента. По-хорошему он должен находится в отдельном сервисе."""

    client = await get_clients_db(session, None, None, email=login_payload.email)
    if not client or client.password != hash_password(login_payload.password):
        raise HTTPException(status_code=401, detail="User not found!")

    token_payload = {'sub': login_payload.email, 'email': login_payload.email}
    auth_token = encode_jwt(token_payload)

    response.set_cookie("auth_token", auth_token)

    return AuthTokenSchema(auth_token=auth_token)


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("auth_token")


@router.post("/{id}/match/")
async def match(
        id: int,
        request: Request,
        session: AsyncSession = Depends(get_session)) -> dict:

    current_user = await get_current_user(request, session)

    result = await create_match_db(id, current_user, session)
    return result
