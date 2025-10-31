import bcrypt
import jwt
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Session

SECRET_KEY = settings.SECRET_KEY

class RegisterView(APIView):
    """
    Регистрация нового пользователя.
    Хеширует пароль и сохраняет пользователя в базе.
    """
    def post(self, request):
        data = request.data

        # Проверка существующего email
        if User.objects.filter(email=data["email"]).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Хеширование пароля
        password = data["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

        # Создание пользователя
        user = User.objects.create(
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            email=data["email"],
            password=hashed,
        )

        return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Логин пользователя.
    Проверяет пароль, создаёт JWT-токен и сохраняет сессию.
    """
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Поиск пользователя
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверка пароля
        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Создание токена JWT
        expire_at = timezone.now() + timedelta(hours=2)
        payload = {"user_id": user.id, "exp": expire_at.timestamp()}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Сохранение сессии
        Session.objects.create(user=user, token=token, expire_at=expire_at)

        return Response({"token": token}, status=status.HTTP_200_OK)