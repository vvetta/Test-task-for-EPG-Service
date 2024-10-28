import uvicorn

from fastapi import FastAPI

from src.api.router import router as client_router


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")


app.include_router(client_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
