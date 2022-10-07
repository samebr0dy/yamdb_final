from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Title, Review, User

from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminOrSuperuser,
                          IsAuthorOrModeratorOrAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          PostTitleSerializer, ReviewSerializer,
                          SignUpSerializer, TitleSerializer, UserSerializer)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('review__score')).all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostTitleSerializer
        return TitleSerializer


class GenreCategoryMixin(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(GenreCategoryMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(GenreCategoryMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение и создание ревью."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.review.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Получение и создание комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        title = get_object_or_404(Title,
                                  pk=self.kwargs.get('title_id'))
        review = get_object_or_404(Review,
                                   title=title,
                                   pk=self.kwargs.get('review_id'))
        return review.comment.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title,
                                  pk=self.kwargs.get('title_id'))
        review = get_object_or_404(Review,
                                   title=title,
                                   pk=self.kwargs.get('review_id'))
        serializer.save(review=review, author=self.request.user)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSuperuser]
    filter_backends = [filters.OrderingFilter]
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def api_get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        token = RefreshToken.for_user(user)
        return Response({'token': str(token.access_token)})
    return Response(
        data='Неверный код подтверждения',
        status=status.HTTP_400_BAD_REQUEST)


@api_view(['Post'])
def api_signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    try:
        user = User.objects.get_or_create(email=email,
                                          username=username)[0]
    except Exception:
        return Response(
            'Такой логин или е-майл уже существует!',
            status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Код подтверждения: {confirmation_code}',
        settings.TEST_EMAIL,
        [user.email])
    return Response(serializer.data, status=status.HTTP_200_OK)
