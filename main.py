import uvicorn

from datetime import datetime
from typing import List, Literal, Optional
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.crud import get_clients_db, get_current_user
from src.api.database import get_session
from src.api.schemas import ClientSchema
from src.api.router import router as client_router


app = FastAPI(root_path="/api", docs_url='/docs', openapi_url='/openapi.json')

app.include_router(client_router)


@app.get("/list", response_model=List[ClientSchema])
async def get_clients_list(
        request: Request,
        gender: Optional[Literal["male", "female"]] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        distance: Optional[float] = None,
        time_created: Optional[datetime] = None,
        sort_order: Optional[Literal["desc", "asc"]] = None,
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


app.mount("/static", StaticFiles(directory="client_photos"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
