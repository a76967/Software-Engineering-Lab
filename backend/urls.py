from django.urls import path, include

urlpatterns = [
    # …other v1 routes…
    path('v1/labels/', include('labels.urls')),
    # …other v1 routes…
]