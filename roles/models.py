from django.db import models

from django.db import models
import uuid



class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

class BusinessElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

class AccessRolesRules(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="access_rules")
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name="access_rules")
    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"


class Meta:
    unique_together = ('role', 'element')
    ordering = ['role__name', 'element__name']