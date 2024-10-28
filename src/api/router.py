from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Form, File, UploadFile, Depends

from src.api.utils import hash_password, add_watermark
from src.api.database import get_session
from src.api.crud import create_client_db
from src.api.schemas import CreateClientSchema, ClientSchema


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
