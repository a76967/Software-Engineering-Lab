import json
import os
import binascii
import hashlib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

def hash_password(password):
    iterations = 600000
    salt = os.urandom(16)
    salt_hex = binascii.hexlify(salt).decode('ascii')
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    hash_hex = binascii.hexlify(dk).decode('ascii')
    return f"pbkdf2_sha256${iterations}${salt_hex}${hash_hex}"

@csrf_exempt
def register_user(request):
    print("register_user endpoint hit!")
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    
    data = json.loads(request.body)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password1")  # Note: we use password1 (and assume password1 == password2)
    role = data.get("role", "").lower()
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    
    if not username or not email or not password:
        return JsonResponse({"error": "Missing required fields"}, status=400)
    
    hashed_password = hash_password(password)
    is_superuser = True if role == "admin" else False
    is_staff = True if role == "admin" else False

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO auth_user
                  (username, password, email, is_superuser, first_name, last_name, is_staff, is_active, date_joined)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id, username, email, first_name, last_name, date_joined;
            """
            cursor.execute(sql, [username, hashed_password, email,
                                   is_superuser, first_name, last_name, is_staff, True])
            row = cursor.fetchone()
        return JsonResponse({
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "first_name": row[3],
            "last_name": row[4],
            "date_joined": row[5]
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)