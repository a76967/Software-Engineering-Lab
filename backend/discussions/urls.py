from django.urls import path
from .views import DiscussionListCreateAPIView, DiscussionDetailAPIView

urlpatterns = [
    path('projects/<int:project_id>/discussions/', DiscussionListCreateAPIView.as_view(), name='discussion_list'),
    path('projects/<int:project_id>/discussions/<int:discussion_id>/', DiscussionDetailAPIView.as_view(), name='discussion_detail'),
]