import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from auth_system_project.roles.models import Role

SECRET_KEY = settings.SECRET_KEY

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email
    
    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])
        Session.objects.filter(user=self).update(expire_at=timezone.now())


    # Пароль
    def set_password(self, raw_password: str):
        self.password = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
        self.save(update_fields=['password'])

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode(), self.password.encode())

    # JWT и сессии
    def generate_jwt(self, expire_hours: int = 2) -> str:
        expire_at = timezone.now() + timedelta(hours=expire_hours)
        token = jwt.encode({"user_id": str(self.id), "exp": expire_at.timestamp()},
                           SECRET_KEY, algorithm="HS256")
        Session.create_for_user(self, token, expire_at)
        return token

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def deactivate(self):
        """Soft delete пользователя"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    @staticmethod
    def decode_jwt(token: str):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    token = models.CharField(max_length=512, unique=True)
    expire_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expire_at']

    def __str__(self):
        return f"{self.user.email} - {self.token[:8]}..."

    @property
    def is_valid(self) -> bool:
        return self.expire_at > timezone.now()

    def revoke(self):
        self.expire_at = timezone.now()
        self.save(update_fields=['expire_at'])

    @classmethod
    def create_for_user(cls, user: User, token: str, expire_at):
        """Создает новую сессию"""
        return cls.objects.create(user=user, token=token, expire_at=expire_at)
