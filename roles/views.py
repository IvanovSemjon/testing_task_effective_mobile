from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Role, BusinessElement, AccessRolesRules
from .serializers import RoleSerializer, BusinessElementSerializer, AccessRolesRulesSerializer

# -------------------------------
# Permissions
# -------------------------------
class IsAdminPermission(permissions.BasePermission):
    """Разрешает доступ только пользователю с ролью 'admin'"""
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user.role, "name", "").lower() == "admin")


class HasAccessPermission(permissions.BasePermission):
    """
    Проверка прав доступа к объекту на основе AccessRolesRules.
    Возвращает 403 если пользователь не имеет прав.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not getattr(user, "role", None):
            return False

        # Админ имеет доступ ко всем объектам
        if user.role.name.lower() == "admin":
            return True

        # Проверка по правилам доступа
        rules = AccessRolesRules.objects.filter(role=user.role, element=obj)
        if not rules.exists():
            return False

        rule = rules.first()
        # Простейшая проверка: если есть read_permission или read_all_permission
        if request.method in permissions.SAFE_METHODS:
            return rule.read_permission or rule.read_all_permission
        elif request.method == "POST":
            return rule.create_permission
        elif request.method in ["PUT", "PATCH"]:
            # Может изменять свои объекты или все
            return rule.update_permission or rule.update_all_permission
        elif request.method == "DELETE":
            return rule.delete_permission or rule.delete_all_permission
        return False

# -------------------------------
# ViewSets
# -------------------------------

class RoleViewSet(viewsets.ModelViewSet):
    """CRUD для ролей. Доступ только для админа"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminPermission]


class BusinessElementViewSet(viewsets.ModelViewSet):
    """CRUD для бизнес-объектов"""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [permissions.IsAuthenticated, HasAccessPermission]

    def get_queryset(self):
        user = self.request.user
        # Админ видит все
        if getattr(user.role, "name", None) == "admin":
            return self.queryset
        # Фильтруем объекты, к которым есть доступ
        allowed_ids = [
            obj.id for obj in self.queryset
            if HasAccessPermission().has_object_permission(self.request, self, obj)
        ]
        return self.queryset.filter(id__in=allowed_ids)


class AccessRolesRulesViewSet(viewsets.ModelViewSet):
    """CRUD для правил доступа. Только админ может управлять"""
    queryset = AccessRolesRules.objects.all()
    serializer_class = AccessRolesRulesSerializer
    permission_classes = [IsAdminPermission]

    @action(detail=False, methods=['get'], url_path='role/(?P<role_id>[^/.]+)')
    def rules_for_role(self, request, role_id=None):
        """Получить все правила конкретной роли"""
        rules = self.queryset.filter(role_id=role_id)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def update_permissions(self, request, pk=None):
        """Обновление разрешений для конкретного правила"""
        rule = self.get_object()
        for field in ["read_permission", "read_all_permission",
                      "create_permission", "update_permission", "update_all_permission",
                      "delete_permission", "delete_all_permission"]:
            if field in request.data:
                setattr(rule, field, request.data[field])
        rule.save()
        return Response({"message": "Rule updated"}, status=status.HTTP_200_OK)