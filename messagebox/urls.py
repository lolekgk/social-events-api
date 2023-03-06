from django.urls import path

from .views import MessageListView

app_name = "messagebox"

urlpatterns = [path("", MessageListView.as_view(), name="message_list")]
