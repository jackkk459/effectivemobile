from django.http import JsonResponse
from django.views import View

from core.services.permissions import has_access


class MockProductsView(View):
    element = "products"

    def get(self, request):
        if not request.user:
            return JsonResponse({}, status=401)

        if not has_access(
            user=request.user,
            element_name=self.element,
            action="read",
        ):
            return JsonResponse({}, status=403)

        return JsonResponse(
            {
                "data": [
                    {"id": 1, "name": "Product 1", "owner_id": 1},
                    {"id": 2, "name": "Product 2", "owner_id": 2},
                ]
            }
        )
