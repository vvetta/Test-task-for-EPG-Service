import os
import jwt
import hashlib
import asyncio
import aiofiles

from io import BytesIO
from fastapi import UploadFile
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor

from src.api.settings import ALGORITHM, public_key, private_key, ACCESS_TOKEN_LIFE_TIME_MINUTES

executor = ThreadPoolExecutor()


def hash_password(password: str) -> str:

    return hashlib.sha256(password.encode()).hexdigest()


async def add_watermark(photo: UploadFile, watermark_text: str = "TEXT") -> BytesIO:
    return await asyncio.get_running_loop().run_in_executor(executor, sync_add_watermark, photo, watermark_text)


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

    decoded = jwt.decode(token, public_key, algorithms=[algorithm])

    return decoded
