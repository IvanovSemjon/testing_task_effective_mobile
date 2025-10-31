from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
import jwt
from auth_system_project.users.models import User, Session
from auth_system_project.config.base import SECRET_KEY


class JWTAuthMiddleware:
    """
    Middleware для поддержки JWT и кастомных сессий.
    Не ломает стандартный login/admin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        # Если стандартный AuthenticationMiddleware уже установил user, оставляем его
        if hasattr(request, "user") and request.user.is_authenticated:
            return

        # По умолчанию — анонимный пользователь
        request.user = AnonymousUser()

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return  # токена нет — оставляем AnonymousUser

        token = auth_header.split(" ")[1]

        # 1️⃣ Проверяем кастомную сессию
        session = Session.objects.filter(token=token).first()
        if session and session.is_valid and session.user.is_active:
            request.user = session.user
            request.user.update_last_login()
            return  # пользователь найден через сессию — больше не проверяем JWT

        # 2️⃣ Пробуем расшифровать JWT
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if user_id:
                user = User.objects.filter(id=user_id, is_active=True).first()
                if user:
                    request.user = user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Если токен невалидный — оставляем AnonymousUser
            pass
