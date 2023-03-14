from django.urls import path

from .views import (
    MessageDetailView,
    MessageListView,
    MessageThreadDetailView,
    MessageThreadListView,
)

app_name = "messagebox"

urlpatterns = [
    path("", MessageListView.as_view(), name="message_list"),
    path("<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path(
        "threads/", MessageThreadListView.as_view(), name="message_thread_list"
    ),
    path(
        "threads/<int:pk>/",
        MessageThreadDetailView.as_view(),
        name="message_thread_detail",
    ),
]
