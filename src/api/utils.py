import os
import jwt
import math
import hashlib
import asyncio
import aiofiles
import aiosmtplib

from io import BytesIO
from pydantic import EmailStr
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from jwt.exceptions import InvalidTokenError
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile, HTTPException

from src.api.models import Client
from src.api.schemas import CreateClientSchema
from src.api.settings import ALGORITHM, public_key, private_key, ACCESS_TOKEN_LIFE_TIME_MINUTES, \
    SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT

executor = ThreadPoolExecutor()


def hash_password(password: str) -> str:

    return hashlib.sha256(password.encode()).hexdigest()


async def add_watermark(photo: UploadFile, watermark_text: str = "TEXT") -> BytesIO:
    return await asyncio.get_running_loop().run_in_executor(executor,
                                                            sync_add_watermark,
                                                            photo,
                                                            watermark_text)


def sync_add_watermark(photo: UploadFile, watermark_text: str) -> BytesIO:
    image = Image.open(photo.file).convert("RGBA")

    watermark = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(watermark)

    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(watermark_text, font)
    position = (image.width - text_width - 10, image.height - text_height - 10)
    draw.text(position, watermark_text, fill=(255, 255, 255, 128), font=font)

    watermarked_image = Image.alpha_composite(image, watermark).convert("RGB")

    output = BytesIO()
    watermarked_image.save(output, format="JPEG")
    output.seek(0)

    return output


async def save_client_photo(photo: BytesIO, client_email: str) -> str:
    os.makedirs("client_photos", exist_ok=True)

    filepath = os.path.join("client_photos", f"{client_email}.jpeg")

    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(photo.read())

    filepath = f"/static/{client_email}.jpeg"

    return filepath


def encode_jwt(payload: dict, private_key: str = private_key,
               algorithm: str = ALGORITHM,
               expire_minutes: int = ACCESS_TOKEN_LIFE_TIME_MINUTES) -> str:

    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    payload.update(exp=expire, iat=now)
    encoded = jwt.encode(payload, private_key, algorithm)

    return encoded


def decode_jwt(token: str, public_key: str = public_key,
               algorithm: str = ALGORITHM) -> dict:

    try:
        decoded = jwt.decode(token, public_key, algorithms=[algorithm])
        return decoded
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Authorization token error.")


def calculate_distance(lat1, lon1, lat2, lon2):

    r = 6371.0

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


async def send_email(recipient_email: EmailStr, subject: str, body: str):

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        print(f"Email sent to {recipient_email}")
    except aiosmtplib.SMTPException as e:
        raise HTTPException(status_code=400, detail=f"Failed to send email to {recipient_email}: {e}")


async def send_mutual_match_email(current_user: CreateClientSchema, target_client: Client) -> dict:
    message_to_current_user = (
        f"Вы понравились {target_client.first_name}! Почта участника: {target_client.email}"
    )
    message_to_target_client = (
        f"Вы понравились {current_user.first_name}! Почта участника: {current_user.email}"
    )

    await send_email(current_user.email, "Взаимная симпатия!", message_to_current_user)
    await send_email(target_client.email, "Взаимная симпатия!", message_to_target_client)

    return {"message": "Mutual match!", "target_email": target_client.email}


def get_cache_key(sort_order: str | None, current_user: CreateClientSchema | None, **kwargs) -> str:
    return f"{current_user.id if current_user else 'anon'}:{sort_order}:{kwargs}"
