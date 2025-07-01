from django.urls import path
from .views import PerspectiveView, PerspectiveItemView

urlpatterns = [
    path(
        "projects/<int:project_id>/perspectives/",
        PerspectiveView.as_view({"get": "list", "post": "create"}),
        name="project-perspectives",
    ),
    path(
        "projects/<int:project_id>/perspectives/<int:pk>/",
        PerspectiveView.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="project-perspective-detail",
    ),
    path(
        "projects/<int:project_id>/perspective-items/",
        PerspectiveItemView.as_view({"get": "list", "post": "create"}),
        name="project-perspective-items",
    ),
    path(
        "projects/<int:project_id>/perspective-items/<int:pk>/",
        PerspectiveItemView.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="project-perspective-item-detail",
    ),
]