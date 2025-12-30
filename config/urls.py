# config/urls.py
from django.urls import path

from api.admin_views import AccessRuleView, AssignRoleView, RoleListView
from api.auth_views import (DeleteAccountView, LoginView, LogoutView,
                            RegisterView)
from api.mock_views import MockProductsView

urlpatterns = [
    # Аутентификация
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/delete/", DeleteAccountView.as_view()),
    # Mock endpoints для демонстрации
    path("mock/products/", MockProductsView.as_view()),
    # Администрирование
    path("admin/roles/", RoleListView.as_view()),
    path("admin/access-rules/", AccessRuleView.as_view()),
    path("admin/assign-role/", AssignRoleView.as_view()),
]
