from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "events"

router = DefaultRouter()
router.register("locations", views.LocationViewSet, basename="locations")
router.register("", views.EventViewSet, basename="events")

urlpatterns = router.urls
