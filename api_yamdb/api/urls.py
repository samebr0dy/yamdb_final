from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitlesViewSet, UsersViewSet, api_get_token,
                    api_signup)

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoryViewSet,
                basename='categories')
router.register('genres', GenreViewSet,
                basename='genres')
router.register('titles', TitlesViewSet,
                basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_get_token),
    path('v1/', include(router.urls)),
]
