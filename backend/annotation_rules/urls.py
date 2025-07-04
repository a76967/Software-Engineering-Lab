from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AnnotationRuleGridViewSet, RuleVoteViewSet, GridVoteViewSet

router = DefaultRouter()
router.register(
    r"projects/(?P<project_pk>\d+)/rule-grids",
    AnnotationRuleGridViewSet,
    basename="project-rule-grids",
)
router.register(
    r"projects/(?P<project_pk>\d+)/rule-votes",
    RuleVoteViewSet,
    basename="project-rule-votes",
)
router.register(
    r"projects/(?P<project_pk>\d+)/grid-votes",
    GridVoteViewSet,
    basename="project-grid-votes",
)

urlpatterns = [path("", include(router.urls))]