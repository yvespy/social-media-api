from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
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
    UserSerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Obtain JWT tokens",
        description="Provide username and password to receive access and refresh tokens",
        request=RegisterSerializer,
        responses={
            200: OpenApiResponse(description="Tokens", response=RegisterSerializer)
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="User registration",
        description="Register a new user with username, email and password",
        responses={201: ProfileSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user's profile",
        responses=ProfileSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update current user's profile",
        request=ProfileSerializer,
        responses=ProfileSerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email", "first_name", "last_name"]

    def get_queryset(self):
        return User.objects.all().prefetch_related(
            "following__following_user",
            "followers__user",
        )

    @extend_schema(
        summary="List users",
        description="Retrieve a list of users with optional search filters",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search by username, email, first_name, last_name",
                required=False,
                type=str,
            )
        ],
        responses=ProfileSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve user by ID",
        responses=ProfileSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class UserFollowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowingSerializer
    queryset = UserFollowing.objects.all()

    def perform_create(self, serializer):
        follower = self.request.user
        following = serializer.validated_data["following_user"]
        if follower == following:
            raise serializers.ValidationError("You can't follow yourself.")
        serializer.save(user=follower)

    @extend_schema(
        summary="Follow a user",
        description="Create a following relationship by providing 'following_user' ID",
        request=FollowingSerializer,
        responses=FollowingSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="List following relationships",
        responses=FollowingSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Unfollow a user",
        description="Unfollow a user by sending POST request with 'following_user' ID",
        request=FollowingSerializer,
        responses={
            204: OpenApiResponse(description="Unfollow successful"),
            400: OpenApiResponse(description="Bad request"),
            404: OpenApiResponse(description="User not found"),
        },
    )
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
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List followers of a user",
        parameters=[
            OpenApiParameter(
                name="pk",
                description="User ID to get followers of",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
        responses=FollowersSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        return UserFollowing.objects.filter(following_user__id=user_id).select_related(
            "user", "following_user"
        )


class UserFollowingList(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List users that a user is following",
        parameters=[
            OpenApiParameter(
                name="pk",
                description="User ID to get following list for",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
        responses=FollowingSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        return UserFollowing.objects.filter(user__id=user_id).select_related(
            "user", "following_user"
        )
