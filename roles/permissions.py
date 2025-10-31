from rest_framework import permissions
from .models import AccessRolesRules, BusinessElement

class HasAccessPermission(permissions.BasePermission):
    """
    Проверяет, есть ли у пользователя доступ к бизнес-объекту.
    Использует таблицу AccessRolesRules.
    """
    def has_object_permission(self, request, view, obj):
        # Анонимные пользователи ничего не видят
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        # Получаем правило для роли пользователя и объекта
        try:
            rule = AccessRolesRules.objects.get(
                role=user.role,
                element=obj.element
            )
        except AccessRolesRules.DoesNotExist:
            return False

        # Различаем методы запроса
        if request.method in permissions.SAFE_METHODS:
            return rule.read_permission or (rule.read_all_permission and obj.owner == user)
        if request.method == "POST":
            return rule.create_permission
        if request.method in ("PUT", "PATCH"):
            return rule.update_permission or (rule.update_all_permission and obj.owner == user)
        if request.method == "DELETE":
            return rule.delete_permission or (rule.delete_all_permission and obj.owner == user)

        return False
