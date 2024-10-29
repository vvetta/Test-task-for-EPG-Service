import uvicorn

from datetime import datetime
from typing import List, Literal
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.crud import get_clients_db
from src.api.database import get_session
from src.api.schemas import ClientSchema
from src.api.router import router as client_router


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.include_router(client_router)


@app.get("/list", response_model=List[ClientSchema])
async def get_clients_list(
        gender: Literal["male", "female"] | None,
        first_name: str | None,
        last_name: str | None,
        time_created: datetime | None,
        sort_order: Literal["desc", "asc"] | None,
        session: AsyncSession = Depends(get_session)) -> List[ClientSchema]:

    clients = await get_clients_db(
        session=session,
        sort_order=sort_order,
        gender=gender,
        first_name=first_name,
        last_name=last_name,
        time_created=time_created)

    return clients


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
