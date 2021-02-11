from rest_framework.authentication import TokenAuthentication
from rest_framework.request import Request


class TokenAuthSupportQueryString(TokenAuthentication):
    """
    Extend the TokenAuthentication class to support querystring authentication.

    It works with the following parameter: "http://www.example.com/?apikey=<token_key>"
    """

    def authenticate(self, request: Request):
        # Check if 'apikey' is in the request query params.
        # Give precedence to 'Authorization' header.
        if (
            "apikey" in request.query_params
            and "HTTP_AUTHORIZATION" not in request.META
        ):
            api_key = request.query_params.get("apikey", "")
            return self.authenticate_credentials(api_key)
        return super(TokenAuthSupportQueryString, self).authenticate(request)
