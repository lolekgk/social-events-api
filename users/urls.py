from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from .views import UserGroupViewSet, UserViewSet

app_name = "users"

router = DefaultRouter()
router.register("", UserViewSet, basename="users")
users_router = NestedDefaultRouter(router, "", lookup="user")
users_router.register("groups", UserGroupViewSet, basename="user-groups")

urlpatterns = router.urls + users_router.urls
