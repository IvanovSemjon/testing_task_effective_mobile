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
    role = models.ForeignKey(Role, on_delete=models.PROTECT)  # нельзя удалить роль, пока есть пользователи
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    # -----------------------
    # Методы работы с паролем
    # -----------------------
    def set_password(self, raw_password: str):
        """Хеширует и сохраняет пароль"""
        self.password = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
        self.save(update_fields=['password'])

    def check_password(self, raw_password: str) -> bool:
        """Проверяет пароль"""
        return bcrypt.checkpw(raw_password.encode(), self.password.encode())

    # -----------------------
    # Методы работы с JWT
    # -----------------------
    def generate_jwt(self, expire_hours: int = 2) -> str:
        """Создает JWT токен и сохраняет сессию"""
        expire_at = timezone.now() + timedelta(hours=expire_hours)
        payload = {"user_id": str(self.id), "exp": expire_at.timestamp()}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Создаем или обновляем сессию
        Session.objects.update_or_create(user=self, defaults={"token": token, "expire_at": expire_at})
        return token

    @staticmethod
    def decode_jwt(token: str):
        """Декодирует токен JWT и возвращает payload"""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    token = models.CharField(max_length=512, unique=True)
    expire_at = models.DateTimeField()

    class Meta:
        ordering = ['-expire_at']

    def __str__(self):
        return f"{self.user.email} - {self.token[:8]}..."

    @property
    def is_valid(self) -> bool:
        """Проверяет, что сессия еще не истекла"""
        return self.expire_at > timezone.now()

    def revoke(self):
        """Аннулирует сессию"""
        self.expire_at = timezone.now()
        self.save(update_fields=['expire_at'])