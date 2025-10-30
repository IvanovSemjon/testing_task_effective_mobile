import bcrypt, jwt, datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Session

SECRET_KEY = settings.SECRET_KEY

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        password = data["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
        user = User.objects.create(
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            email=data["email"],
            password=hashed,
        )
        return Response({"message": "User registered"}, status=201)


class LoginView(APIView):
    def post(self, request):
        user = User.objects.filter(email=request.data["email"]).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        if not bcrypt.checkpw(request.data["password"].encode("utf-8"), user.password.encode("utf-8")):
            return Response({"error": "Invalid password"}, status=401)

        payload = {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        Session.objects.create(user=user, token=token, expire_at=datetime.datetime.utcnow() + datetime.timedelta(hours=2))

        return Response({"token": token})
