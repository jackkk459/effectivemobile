import json

from django.http import JsonResponse
from django.views import View

from core.models import AccessRule, BusinessElement, Role, User, UserRole
from core.services.permissions import has_access


class RoleListView(View):
    element = "roles"

    def get(self, request):
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not has_access(
            user=request.user, element_name=self.element, action="read_all"
        ):
            return JsonResponse({"error": "Forbidden"}, status=403)

        roles = Role.objects.all().values("id", "name")
        return JsonResponse({"roles": list(roles)})

    def post(self, request):
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not has_access(
            user=request.user, element_name=self.element, action="create"
        ):
            return JsonResponse({"error": "Forbidden"}, status=403)

        try:
            data = json.loads(request.body)
            role = Role.objects.create(name=data["name"])
            return JsonResponse({"id": role.id, "name": role.name})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class AccessRuleView(View):
    element = "access_rules"

    def get(self, request):
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not has_access(
            user=request.user, element_name=self.element, action="read_all"
        ):
            return JsonResponse({"error": "Forbidden"}, status=403)

        rules = AccessRule.objects.select_related("role", "element").all()
        data = []
        for rule in rules:
            data.append(
                {
                    "id": rule.id,
                    "role": rule.role.name,
                    "element": rule.element.name,
                    "read": rule.read_permission,
                    "read_all": rule.read_all_permission,
                    "create": rule.create_permission,
                    "update": rule.update_permission,
                    "update_all": rule.update_all_permission,
                    "delete": rule.delete_permission,
                    "delete_all": rule.delete_all_permission,
                }
            )
        return JsonResponse({"rules": data})

    def post(self, request):
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not has_access(
            user=request.user, element_name=self.element, action="create"
        ):
            return JsonResponse({"error": "Forbidden"}, status=403)

        try:
            data = json.loads(request.body)
            role = Role.objects.get(id=data["role_id"])
            element = BusinessElement.objects.get(id=data["element_id"])

            rule, created = AccessRule.objects.update_or_create(
                role=role,
                element=element,
                defaults={
                    "read_permission": data.get("read", False),
                    "read_all_permission": data.get("read_all", False),
                    "create_permission": data.get("create", False),
                    "update_permission": data.get("update", False),
                    "update_all_permission": data.get("update_all", False),
                    "delete_permission": data.get("delete", False),
                    "delete_all_permission": data.get("delete_all", False),
                },
            )
            return JsonResponse(
                {
                    "id": rule.id,
                    "created": created,
                    "role": role.name,
                    "element": element.name,
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class AssignRoleView(View):
    element = "users"

    def post(self, request):
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        if not has_access(
            user=request.user, element_name=self.element, action="update_all"
        ):
            return JsonResponse({"error": "Forbidden"}, status=403)

        try:
            data = json.loads(request.body)
            user = User.objects.get(id=data["user_id"])
            role = Role.objects.get(id=data["role_id"])

            UserRole.objects.get_or_create(user=user, role=role)
            return JsonResponse(
                {
                    "user_id": user.id,
                    "role_id": role.id,
                    "message": "Role assigned successfully",
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
