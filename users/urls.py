from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt import views
from users.views import RegisterView, ProfileViewSet

router = SimpleRouter()
router.register(r"profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("token/", views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="auth_register"),
] + router.urls
