import fastapi
import fastapi.security
from starlette import status

from dht_torznab.settings import get_settings

API_KEY_QUERY = fastapi.security.APIKeyQuery(name="apikey")


def verify_api_key(api_key: str = fastapi.Security(API_KEY_QUERY)) -> None:
    """FastAPI dependency to verify API key in query parameter.

    Args:
        api_key: API key string from query parameter.

    Raises:
        fastapi.HTTPException: when the API key is invalid.
    """
    if api_key != get_settings().API.KEY.get_secret_value():
        raise fastapi.HTTPException(status.HTTP_403_FORBIDDEN)
