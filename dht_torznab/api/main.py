import uvicorn
from fastapi import Depends, FastAPI

from dht_torznab.api import endpoints
from dht_torznab.api.security import verify_api_key

app = FastAPI(dependencies=[Depends(verify_api_key)])

app.include_router(endpoints.router, prefix="/torznab")


if __name__ == "__main__":
    uvicorn.run("dht_torznab.api.main:app", port=8080, log_level="info", reload=True)
