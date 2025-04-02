<<<<<<< HEAD
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
=======
import os
import binascii
import hashlib
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status
>>>>>>> Goncalo
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response({"username": request.user.username})

<<<<<<< HEAD

class Users(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("username",)


class UserCreation(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED, headers=headers
        )
=======

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def hash_password(self, password):
        iterations = 600000
        salt = os.urandom(16)
        salt_hex = binascii.hexlify(salt).decode('ascii')
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        hash_hex = binascii.hexlify(dk).decode('ascii')
        return f"pbkdf2_sha256${iterations}${salt_hex}${hash_hex}"
>>>>>>> Goncalo

    def post(self, request, *args, **kwargs):
        data = request.data

<<<<<<< HEAD

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
=======
        username = data.get('username')
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')
        role = data.get('role', '').lower()
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not username or not email or not password1 or not password2:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = self.hash_password(password1)
        
        is_superuser = True if role == 'admin' else False
        is_staff = True if role == 'admin' else False

        print("RegisterView: about to execute raw SQL insertion")
        try:
            with connection.cursor() as cursor:
                sql = """
                  INSERT INTO auth_user 
                    (username, password, email, is_superuser, first_name, last_name, is_staff, is_active, date_joined)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                  RETURNING id, username, email, first_name, last_name, date_joined;
                """
                cursor.execute(sql, [
                    username,
                    hashed_password,
                    email,
                    is_superuser,
                    first_name,
                    last_name,
                    is_staff,
                    True
                ])
                row = cursor.fetchone()
            print("RegisterView: raw SQL executed successfully, row returned:", row)

            new_user = {
                "username": row[1],
                "email": row[2],
                "plain_password": password1,
                "is_superuser": is_superuser
            }

            print("Registration successful. Now calling email helper.")
            send_registration_email_manual(
                new_user["username"],
                new_user["email"],
                new_user["plain_password"],
                new_user["is_superuser"],
            )
            print("Email helper call returned")

            return Response({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "first_name": row[3],
                "last_name": row[4],
                "date_joined": row[5]
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("RegisterView error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    
    data = json.loads(request.body)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password1")
    role = data.get("role", "").lower()
    is_superuser = True if role == "admin" else False
    
    new_user = {
        "username": username,
        "email": email,
        "plain_password": password,
        "is_superuser": is_superuser,
    }
    
    subject = 'Your doccana access credentials! 🦭'
    body = (
        "Welcome to doccana! 😊\n\n"
        "Here are your access credentials to our Doccana web-app:\n\n"
        f"• Username: {username}\n"
        f"• Password: {password}\n\n"
        f"You are an {'Admin' if is_superuser else 'Annotator'}.\n\n"
        "Please keep these details in a safe place 🔒. If you have any doubts or issues logging in, feel free to reach out to us! 📩\n\n"
        "Best regards,\n"
        "The doccana Team 💻✨"
    )
    
    return JsonResponse(new_user, status=201)
>>>>>>> Goncalo
