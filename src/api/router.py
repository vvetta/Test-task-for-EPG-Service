from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Form, File, UploadFile, Depends, Response, HTTPException

from src.api.utils import hash_password, add_watermark, encode_jwt
from src.api.database import get_session
from src.api.crud import create_client_db, get_clients_db
from src.api.schemas import CreateClientSchema, ClientSchema, LoginClientSchema, AuthTokenSchema


router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/create", response_model=ClientSchema)
async def create_client(
        email: EmailStr = Form(...),
        password: str = Form(...),
        photo: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)) -> ClientSchema:

    client = CreateClientSchema(
        email=email,
        password=hash_password(password))

    photo_w_wm = await add_watermark(photo)

    client = await create_client_db(session, client, photo_w_wm)

    return client


@router.post("/login", response_model=AuthTokenSchema)
async def login(login_payload: LoginClientSchema,
                response: Response,
                session: AsyncSession = Depends(get_session)) -> AuthTokenSchema:
    """Эндпоинт авторизации клиента. По-хорошему он должен находится в отдельном сервисе."""

    client = await get_clients_db(session, None, email=login_payload.email)
    if not client or client.password != hash_password(login_payload.password):
        raise HTTPException(status_code=401, detail="User not found!")

    token_payload = {'sub': login_payload.email, 'email': login_payload.email}
    auth_token = encode_jwt(token_payload)

    response.set_cookie("auth_token", auth_token)

    return AuthTokenSchema(auth_token=auth_token)


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("auth_token")
