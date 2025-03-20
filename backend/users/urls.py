from django.urls import include, path
from django.http import JsonResponse

from .views import Me
from users.register import register_user

def register(request):
    return JsonResponse({"message": "Register endpoint"})

urlpatterns = [
    path("me", Me.as_view(), name="me"),
    path("register/", register_user, name="register"),
]