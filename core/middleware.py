from django.http import HttpRequest

from core.services.token import verify_token


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.user = None

        header = request.headers.get("Authorization")
        if header and header.startswith("Bearer "):
            token = header.split(" ", 1)[1]
            request.user = verify_token(token)

        return self.get_response(request)
