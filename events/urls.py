from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('locations', views.LocationViewSet, basename='locations')
router.register('', views.EventViewSet, basename='events')

urlpatterns = router.urls
