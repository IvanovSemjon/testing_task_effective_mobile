from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_system_project.users.models import User
from auth_system_project.roles.models import Role, AccessRolesRules

# Пример "минимальных объектов бизнес-приложения"
MOCK_OBJECTS = [
    {"id": 1, "name": "Order #1", "owner_id": None},
    {"id": 2, "name": "Order #2", "owner_id": None},
    {"id": 3, "name": "Product A", "owner_id": None},
    {"id": 4, "name": "Product B", "owner_id": None},
]

class BusinessObjectsView(APIView):
    """
    Эндпоинт для получения списка объектов бизнес-приложения.
    Доступ контролируется ролями.
    """
    def get(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем правила доступа для роли пользователя
        rules = AccessRolesRules.objects.filter(role=user.role)
        # В реальном приложении здесь бы проверяли read_permission
        allowed_objects = []
        for obj in MOCK_OBJECTS:
            # Проверяем: может ли пользователь читать все объекты
            if any(rule.read_all_permission for rule in rules):
                allowed_objects.append(obj)
            # Проверяем: может ли пользователь читать свои объекты
            elif any(rule.read_permission and obj.get("owner_id") == user.id for rule in rules):
                allowed_objects.append(obj)

        if not allowed_objects:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        return Response({"objects": allowed_objects}, status=status.HTTP_200_OK)


class BusinessObjectDetailView(APIView):
    """
    Получение одного объекта по ID.
    """
    def get(self, request, obj_id):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        obj = next((o for o in MOCK_OBJECTS if o["id"] == obj_id), None)
        if not obj:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверка доступа
        rules = AccessRolesRules.objects.filter(role=user.role)
        can_read = any(rule.read_all_permission for rule in rules) or \
                   any(rule.read_permission and obj.get("owner_id") == user.id for rule in rules)
        if not can_read:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        return Response({"object": obj}, status=status.HTTP_200_OK)