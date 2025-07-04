from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from .models import Perspective, PerspectiveItem, AdminPerspective
from .serializers import (
    PerspectiveSerializer,
    PerspectiveItemSerializer,
    AdminPerspectiveSerializer,
)
from .models import Perspective, PerspectiveItem
from .serializers import PerspectiveSerializer, PerspectiveItemSerializer
from projects.models import Project
from projects.permissions import IsProjectAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated


class PerspectiveView(viewsets.ModelViewSet):
    serializer_class = PerspectiveSerializer

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return Perspective.objects.filter(project_id=project_id)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get("project_id")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_perspective = request.data.get("admin_perspective")
        serializer.save(project=project, admin_perspective_id=admin_perspective)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PerspectiveItemView(viewsets.ModelViewSet):
    serializer_class = PerspectiveItemSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated & IsProjectAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        queryset = PerspectiveItem.objects.filter(project_id=project_id)
        admin_perspective = self.request.query_params.get("admin_perspective")
        if admin_perspective:
            queryset = queryset.filter(admin_perspective_id=admin_perspective)
        return queryset

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        admin_perspective = self.request.data.get("admin_perspective")
        serializer.save(project_id=project_id, admin_perspective_id=admin_perspective)

class AdminPerspectiveView(viewsets.ModelViewSet):
    serializer_class = AdminPerspectiveSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated & IsProjectAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return AdminPerspective.objects.filter(project_id=project_id)
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        if AdminPerspective.objects.filter(project_id=project_id).exists():
            raise ValidationError("Admin perspective already exists for this project.")
        serializer.save(project_id=project_id)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Perspective.objects.filter(admin_perspective=instance).delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def countries(request):
    """Return list of country names"""
    try:
        import pycountry
    except ImportError:
        return Response(
            {"detail": "pycountry package not installed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    country_names = sorted([c.name for c in pycountry.countries])
    return Response(country_names)