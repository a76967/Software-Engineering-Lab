from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AnnotationRuleGridViewSet

router = DefaultRouter()
router.register(
    r"projects/(?P<project_pk>\d+)/rule-grids",
    AnnotationRuleGridViewSet,
    basename="project-rule-grids",
)

urlpatterns = [path("", include(router.urls))]