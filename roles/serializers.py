from rest_framework import serializers
from .models import Role, BusinessElement, AccessRolesRules




# Сериализатор для роли
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# Сериализатор для бизнес-объекта
class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = '__all__'

# Сериализатор для правил доступа
class AccessRolesRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRolesRules
        fields = '__all__'
