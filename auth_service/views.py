from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Registration
from django.contrib.auth.hashers import make_password, check_password

class SignupAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if Registration.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=400)

        user = Registration(username=username, email=email, password=make_password(password))
        user.save()
        return Response({"message": "User registered successfully"})

class LoginAPI(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = Registration.objects.get(email=email)
            if check_password(password, user.password):
                return Response({"message": "Login successful", "user_id": user.id})
            else:
                return Response({"error": "Invalid password"}, status=400)
        except Registration.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
