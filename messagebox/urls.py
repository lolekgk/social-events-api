from rest_framework.routers import DefaultRouter

from .views import MessageThreadViewSet, MessageViewSet

app_name = "messagebox"
router = DefaultRouter()
router.register("threads", MessageThreadViewSet, basename="threads")
router.register("", MessageViewSet, basename="messagebox")

urlpatterns = router.urls
