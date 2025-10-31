import bcrypt
import jwt
import uuid
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from .models import User, Session
from .serializers import UserSerializer

SECRET_KEY = settings.SECRET_KEY


# -------------------------
# Регистрация пользователя
# -------------------------
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        required_fields = ["first_name", "email", "password", "password_repeat"]

        for field in required_fields:
            if field not in data:
                return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

        if data["password"] != data["password_repeat"]:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=data["email"]).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем пользователя с ролью "user" по умолчанию
        from auth_system_project.roles.models import Role
        user_role = Role.objects.filter(name="user").first()
        if not user_role:
            return Response({"error": "Default user role not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()

        user = User.objects.create(
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            email=data["email"],
            password=hashed,
            role=user_role,
        )

        return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)


# -------------------------
# Логин пользователя
# -------------------------
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return Response({"error": "User not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Создаем JWT и сессию
        expire_at = timezone.now() + timedelta(hours=2)
        payload = {"user_id": str(user.id), "exp": expire_at.timestamp()}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        Session.objects.create(user=user, token=token, expire_at=expire_at)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response({"token": token}, status=status.HTTP_200_OK)


# -------------------------
# Logout пользователя
# -------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Аннулируем все сессии пользователя
        Session.objects.filter(user=request.user).update(expire_at=timezone.now())
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)


# -------------------------
# Обновление профиля
# -------------------------
class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        updated = False
        if "first_name" in data:
            user.first_name = data["first_name"]
            updated = True
        if "last_name" in data:
            user.last_name = data["last_name"]
            updated = True
        if "password" in data:
            hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
            user.password = hashed
            updated = True

        if updated:
            user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data)


# -------------------------
# Soft-delete пользователя
# -------------------------
class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])

        # Аннулируем все сессии
        Session.objects.filter(user=user).update(expire_at=timezone.now())
        return Response({"message": "User deactivated"}, status=status.HTTP_200_OK)