from django.urls import include, path
from django.http import JsonResponse

<<<<<<< HEAD
from .views import Me, UserCreation, UserDetail, Users

urlpatterns = [
    path("me", Me.as_view(), name="me"),
    path("users/", Users.as_view(), name="user-list"),
    path("users/create", UserCreation.as_view(), name="user_create"),
    path("auth/", include("dj_rest_auth.urls")),
    path("users/<int:pk>/", UserDetail.as_view(), name="user-detail"),
]
=======
from .views import Me
from users.register import register_user

def register(request):
    return JsonResponse({"message": "Register endpoint"})

urlpatterns = [
    path("me", Me.as_view(), name="me"),
    path("register/", register_user, name="register"),
]
>>>>>>> Goncalo
