from django.urls import include, path
from django.http import JsonResponse

from .views import Me, UserCreation, Users, UserDetail, RegisterView
from users.register import register_user

def register(request):
    return JsonResponse({"message": "Register endpoint"})

urlpatterns = [
    path("me", Me.as_view(), name="me"),
    path('users/', Users.as_view(), name='user-list'),
    path("users/create", UserCreation.as_view(), name="user_create"),
    path("register/", register_user, name="register"),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
]