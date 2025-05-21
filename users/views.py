from rest_framework import generics, mixins, viewsets, serializers, filters
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User, UserFollowing
from users.serializers import (
    ProfileSerializer,
    RegisterSerializer,
    MyTokenObtainPairSerializer,
    FollowersSerializer,
    FollowingSerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ProfileViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email", "first_name", "last_name"]


class UserFollowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = FollowingSerializer
    queryset = UserFollowing.objects.all()

    def perform_create(self, serializer):
        follower = self.request.user
        following = serializer.validated_data["following_user"]
        if follower == following:
            raise serializers.ValidationError("You can't follow yourself.")
        serializer.save(user=follower)

    @action(detail=False, methods=["post"], url_path="unfollow")
    def unfollow(self, request):
        user = request.user
        following_user_id = request.data.get("following_user")

        if not following_user_id:
            return Response({"error": "Missing following_user id."}, status=400)

        try:
            following = User.objects.get(id=following_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        try:
            follow_instance = UserFollowing.objects.get(
                user=user, following_user=following
            )
            follow_instance.delete()
            return Response(
                {"success": f"You have unfollowed {following.username}."}, status=204
            )
        except UserFollowing.DoesNotExist:
            return Response({"error": "You are not following this user."}, status=400)


class UserFollowersList(generics.ListAPIView):
    serializer_class = FollowersSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        return UserFollowing.objects.filter(following_user__id=user_id)


class UserFollowingList(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        return UserFollowing.objects.filter(user__id=user_id)
