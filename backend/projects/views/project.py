from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from projects.models import Project
from django.db import models
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from projects.serializers import ProjectPolymorphicSerializer


class ProjectList(generics.ListCreateAPIView):
    serializer_class = ProjectPolymorphicSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ["name", "created_at", "created_by", "project_type"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [
                IsAuthenticated,
            ]
        else:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        return Project.objects.filter(role_mappings__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        project.add_admin()

    def delete(self, request, *args, **kwargs):
        delete_ids = request.data["ids"]
        projects = Project.objects.filter(
            role_mappings__user=self.request.user,
            role_mappings__role__name=settings.ROLE_PROJECT_ADMIN,
            pk__in=delete_ids,
        )
        # Todo: I want to use bulk delete.
        # But it causes the constraint error.
        # See https://github.com/django-polymorphic/django-polymorphic/issues/229
        for project in projects:
            project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectPolymorphicSerializer
    lookup_url_kwarg = "project_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]


class CloneProject(views.APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        cloned_project = project.clone()
        serializer = ProjectPolymorphicSerializer(cloned_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectVersionListCreate(views.APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        root = project.root_project or project
        versions = Project.objects.filter(models.Q(pk=root.pk) | models.Q(root_project=root)).order_by("version_number")
        serializer = ProjectPolymorphicSerializer(versions, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        new_project = project.clone()
        serializer = ProjectPolymorphicSerializer(new_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)