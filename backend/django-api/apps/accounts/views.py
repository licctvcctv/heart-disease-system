from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, UserProfileSerializer
from .services import AuthService


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        result = AuthService.authenticate_user(payload["username"], payload["password"])
        if result is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        user_serializer = UserProfileSerializer(result["user"])
        return Response({"token": result["token"], "user": user_serializer.data})
