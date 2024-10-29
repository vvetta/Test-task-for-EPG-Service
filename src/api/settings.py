import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL: str = f"postgresql+asyncpg://{os.getenv("PG_NAME")}:{os.getenv("PG_PASSWORD")}@ \
                    {os.getenv("PG_HOST")}:{os.getenv("PG_PORT")}/{os.getenv("PG_NAME")}"
DATABASE_ECHO: bool = False


ALGORITHM: str = "RS256"
ACCESS_TOKEN_LIFE_TIME_MINUTES: int = 60


def get_private_key() -> str:
    with open("src/certs/jwtRS256.key", "r") as key:
        return key.read()


def get_public_key() -> str:
    with open("shared_data/jwtRS256.key.pub", "r") as key:
        return key.read()


private_key = get_private_key()
public_key = get_public_key()


DAILY_LIKE_LIMIT = 5


SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
