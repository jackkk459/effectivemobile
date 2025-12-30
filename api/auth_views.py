import json

from django.http import JsonResponse
from django.views import View

from core.services.auth import (login_user, logout_user, register_user,
                                soft_delete_user)


class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        user = register_user(**data)
        return JsonResponse({"id": user.id})


class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        token = login_user(data["email"], data["password"])
        if not token:
            return JsonResponse({"error": "invalid credentials"}, status=401)
        return JsonResponse({"token": token})


class LogoutView(View):
    def post(self, request):
        if not request.user:
            return JsonResponse({}, status=401)
        logout_user(request.user)
        return JsonResponse({})


class DeleteAccountView(View):
    def delete(self, request):
        if not request.user:
            return JsonResponse({}, status=401)
        soft_delete_user(request.user)
        return JsonResponse({})
