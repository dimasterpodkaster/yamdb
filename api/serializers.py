from rest_framework import serializers
from .models import User, Category, Genre, Title, Review, Comment
from collections import OrderedDict


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    confirmation_code = serializers.IntegerField()


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password', 'confirmation_code')

    def to_representation(self, instance):
        if isinstance(instance, dict) or isinstance(instance, OrderedDict):
            return instance  # Возвращаем, если это словарь
        return {'email': instance.email}


class RoleUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'username', 'bio', 'email', 'role', 'confirmation_code')
        model = User

    def to_representation(self, instance):
        data = {'id': instance.id, 'first_name': instance.first_name, 'last_name': instance.last_name,
                'username': instance.username, 'bio': instance.bio, 'email': instance.email, 'role': instance.role}
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = {'name', 'slug'}
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        data = {'name': instance.name, 'slug': instance.slug}
        return data


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = {'id', 'name', 'slug'}
        model = Genre
        fields = '__all__'

    def to_representation(self, instance):
        data = {'name': instance.name, 'slug': instance.slug}
        return data


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        fields = {'id', 'name', 'year', 'rating', 'description', 'category', 'genre'}
        model = Title
        fields = '__all__'
        ordering = ['name']

    # def to_representation(self, instance):
    #     data = {'name': instance.name, 'year': instance.year,
    #             'description': instance.description, 'genre': instance.genre.all(), 'category': instance.category}
    #     return data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        fields = {'id', 'text', 'author', 'score', 'pub_date', 'title_id'}
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = {'id', 'text', 'author', 'pub_date', 'review_id'}
        model = Comment
