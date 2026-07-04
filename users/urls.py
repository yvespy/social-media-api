from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenBlacklistView

from users.views import (
    RegisterView,
    ProfileViewSet,
    UserFollowingViewSet,
    UserFollowersList,
    UserFollowingList,
    UserViewSet,
)

router = SimpleRouter()
router.register(r"", UserViewSet, basename="users")
router.register(r"follow", UserFollowingViewSet, basename="follow")

urlpatterns = [
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="auth_register"),
    path(
        "profile/",
        ProfileViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="profile",
    ),
    path("<int:pk>/followers/", UserFollowersList.as_view(), name="followers"),
    path("<int:pk>/following/", UserFollowingList.as_view(), name="following"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
] + router.urls
