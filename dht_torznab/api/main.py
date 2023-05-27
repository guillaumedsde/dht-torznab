import uvicorn
from fastapi import FastAPI

from dht_torznab.api import endpoints

app = FastAPI()

app.include_router(endpoints.router, prefix="/torznab")


if __name__ == "__main__":
    uvicorn.run("dht_torznab.api.main:app", port=8080, log_level="info", reload=True)
