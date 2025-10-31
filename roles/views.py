from rest_framework import viewsets, permissions
from .models import Role, BusinessElement, AccessRolesRules
from .serializers import RoleSerializer, BusinessElementSerializer, AccessRolesRulesSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


# чтобы только admin имел доступ
class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user.role, "name", None) == "admin")


# ViewSet для ролей
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminPermission]

# ViewSet для бизнес-объектов
class BusinessElementViewSet(viewsets.ModelViewSet):
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdminPermission]

# ViewSet для правил доступа
class AccessRolesRulesViewSet(viewsets.ModelViewSet):
    queryset = AccessRolesRules.objects.all()
    serializer_class = AccessRolesRulesSerializer
    permission_classes = [IsAdminPermission]

    # Дополнительный action для получения правил конкретной роли
    @action(detail=False, methods=['get'], url_path='role/(?P<role_id>[^/.]+)')
    def rules_for_role(self, request, role_id=None):
        rules = self.queryset.filter(role_id=role_id)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)
