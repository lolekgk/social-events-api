from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    MessageThreadDetailView,
    MessageThreadListView,
    MessageViewSet,
)

app_name = "messagebox"
router = DefaultRouter()
router.register("", MessageViewSet, basename="messagebox")

urlpatterns = [
    *router.urls,
    path(
        "threads/", MessageThreadListView.as_view(), name="message_thread_list"
    ),
    path(
        "threads/<int:pk>/",
        MessageThreadDetailView.as_view(),
        name="message_thread_detail",
    ),
]
