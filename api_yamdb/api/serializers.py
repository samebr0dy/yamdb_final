from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    username = serializers.CharField(
        max_length=150,  # нужно проверить на регулярку (^[\w.@+-]+\z)
        required=True
    )

    class Meta:
        fields = ('email', 'username',)
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Логин недоступен')
        return value


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,  # нужно проверить на регулярку (^[\w.@+-]+\z)
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=254,
        required=True
    )


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class PostTitleSerializer(TitleSerializer):
    """Сериализатор для POST и UPDATE запросов."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )


class CreateTitleDefault(object):
    """Получение произведения"""
    requires_context = True

    def __call__(self, serializer_field):
        view = serializer_field.context['view']
        title_id = view.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для ревью."""

    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault(),
                              )
    title = serializers.HiddenField(
        default=serializers.CreateOnlyDefault(CreateTitleDefault())
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title',)
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(), fields=['author', 'title']
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = SlugRelatedField(slug_field='username', read_only=True, )

    class Meta:
        fields = '__all__'
        read_only_fields = ('review',)
        model = Comment
