import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL: str = f"postgresql+asyncpg://{os.getenv("PG_NAME")}:{os.getenv("PG_PASSWORD")}@ \
                    {os.getenv("PG_HOST")}:{os.getenv("PG_PORT")}/{os.getenv("PG_NAME")}"
DATABASE_ECHO: bool = False
