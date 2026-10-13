from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .serializers import AuthResponseSerializer, LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Авторизация"],
        summary="Зарегистрироваться по email",
        request=RegisterSerializer,
        responses={201: AuthResponseSerializer},
        examples=[
            OpenApiExample(
                "Регистрация без телефона",
                value={
                    "email": "student@example.com",
                    "password": "StudyPassword!2026",
                    "password_confirm": "StudyPassword!2026",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
            token = Token.objects.create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Авторизация"],
        summary="Войти по email и паролю",
        request=LoginSerializer,
        responses={200: AuthResponseSerializer},
        examples=[
            OpenApiExample(
                "Вход",
                value={"email": "student@example.com", "password": "StudyPassword!2026"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Авторизация"], summary="Посмотреть своего пользователя")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user
