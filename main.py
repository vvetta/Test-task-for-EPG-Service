import uvicorn

from datetime import datetime
from typing import List, Literal
from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.crud import get_clients_db
from src.api.database import get_session
from src.api.schemas import ClientSchema
from src.api.router import router as client_router
from src.api.utils import get_current_user


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.include_router(client_router)


@app.get("/list", response_model=List[ClientSchema])
async def get_clients_list(
        gender: Literal["male", "female"] | None,
        first_name: str | None,
        last_name: str | None,
        distance: float | None,
        time_created: datetime | None,
        sort_order: Literal["desc", "asc"] | None,
        request: Request,
        session: AsyncSession = Depends(get_session)) -> List[ClientSchema]:

    current_user = await get_current_user(request, session)

    clients = await get_clients_db(
        session=session,
        sort_order=sort_order,
        current_user=current_user,
        gender=gender,
        first_name=first_name,
        last_name=last_name,
        time_created=time_created,
        distance=distance)

    return clients


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
