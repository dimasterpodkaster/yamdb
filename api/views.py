from warnings import filters

from django.shortcuts import render, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import (RegistrationSerializer, LoginSerializer, RoleUserSerializer, CategorySerializer,
                             GenreSerializer, TitleSerializer)
from api.permissions import IsSuperUserOrAdmin, IsAdminOrReadOnly, ReadOnly
from api.models import User, Category, Genre, Title
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import PBKDF2PasswordHasher
import random
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.template.defaultfilters import slugify


# Create your views here.
class RegistrationAPIView(APIView):
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        hasher = PBKDF2PasswordHasher()
        data = request.data
        _mutable = data._mutable
        data._mutable = True
        email = data.get('email')
        data['username'] = email
        data['role'] = User.AN
        data['password'] = hasher.encode('12345', hasher.salt())
        verification_code = random.randint(100000, 999999)
        data['confirmation_code'] = verification_code
        data._mutable = _mutable

        # Паттерн создания сериализатора, валидации и сохранения
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if hasattr(data, 'email'):
                subject = 'welcome to YaMDB world'
                message = 'Hi ' + data.get('email') + (', thank you for registering in YaMDB. '
                                                       'There is your verification code: ') + str(verification_code)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [data.get('email'), ]
                send_mail(subject, message, email_from, recipient_list)
            # else:
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if data['email'] and data['confirmation_code']:
                current_user = get_object_or_404(User, email=data['email'])
                if current_user.confirmation_code == int(data['confirmation_code']):
                    current_user.role = User.LG
                    current_user.save(update_fields=['role'])
                    token = AccessToken.for_user(current_user)
                    refresh_token = RefreshToken.for_user(current_user)
                    return Response({'refresh_token': str(refresh_token), 'token': str(token)},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RoleUserSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    pagination_class = PageNumberPagination

    def list(self, request):
        users = self.queryset.all()
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RoleUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        _mutable = data._mutable
        data._mutable = True
        verification_code = random.randint(100000, 999999)
        data['confirmation_code'] = verification_code
        if 'role' not in data:
            data['role'] = User.LG
        data._mutable = _mutable
        serializer = self.get_serializer(data=request.data)
        print(data)
        if serializer.is_valid():
            if hasattr(data, 'email'):
                subject = 'welcome to YaMDB world'
                message = 'Hi ' + data.get('email') + (', thank you for registering in YaMDB. '
                                                       'There is your verification code: ') + str(verification_code)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [data.get('email'), ]
                send_mail(subject, message, email_from, recipient_list)
            # else:
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        users = self.queryset.all()
        user = get_object_or_404(users, username=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        users = self.queryset.all()
        user = get_object_or_404(users, username=pk)
        serializer = RoleUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        users = self.queryset.all()
        user = get_object_or_404(users, username=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PersonalViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RoleUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def list(self, request):
        users = self.queryset.all()
        user = get_object_or_404(users, email=request.user.email)
        serializer = RoleUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        users = self.queryset.all()
        user = get_object_or_404(users, email=request.user.email)
        # print(user.username)
        data = request.data
        _mutable = data._mutable
        data._mutable = True
        data['role'] = user.role
        data._mutable = _mutable
        serializer = RoleUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Category.objects.all()
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name=search)
        return queryset

    def list(self, request):
        categories = self.get_queryset().all().order_by('name')
        page = self.paginate_queryset(categories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RoleUserSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if hasattr(request.user, 'role'):
            if not (request.user.is_superuser or request.user.role == 'admin'):
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            if not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data
        _mutable = data._mutable
        data._mutable = True
        if 'slug' not in data:
            data['slug'] = slugify(data.get('name'))
        data._mutable = _mutable
        serializer = self.get_serializer(data=request.data)
        # print(data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if hasattr(request.user, 'role'):
            if not (request.user.is_superuser or request.user.role == 'admin'):
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            if not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
        categories = self.queryset.all()
        category = get_object_or_404(categories, slug=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Genre.objects.all()
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name=search)
        return queryset

    def list(self, request):
        genres = self.get_queryset().all().order_by('name')
        page = self.paginate_queryset(genres)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RoleUserSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if hasattr(request.user, 'role'):
            if not (request.user.is_superuser or request.user.role == 'admin'):
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            if not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data
        _mutable = data._mutable
        data._mutable = True
        if 'slug' not in data:
            data['slug'] = slugify(data.get('name'))
        data._mutable = _mutable
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if hasattr(request.user, 'role'):
            if not (request.user.is_superuser or request.user.role == 'admin'):
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            if not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
        genres = self.queryset.all()
        genre = get_object_or_404(genres, slug=pk)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class TitleViewSet(viewsets.ModelViewSet):
#     queryset = Title.objects.all()
#     serializer_class = TitleSerializer
#     permission_classes = (IsAdminOrReadOnly,)
#     pagination_class = PageNumberPagination
#
#     def list(self, request):
#         titles = self.queryset.all().order_by('name')
#         page = self.paginate_queryset(titles)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = RoleUserSerializer(titles, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def retrieve(self, request, pk=None):
#         titles = self.queryset.all()
#         title = get_object_or_404(titles, id=pk)
#         serializer = self.get_serializer(title)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def create(self, request):
#         if not request.user.is_authenticated:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         if hasattr(request.user, 'role'):
#             if not (request.user.is_superuser or request.user.role == 'admin'):
#                 return Response(status=status.HTTP_403_FORBIDDEN)
#         else:
#             if not request.user.is_superuser:
#                 return Response(status=status.HTTP_403_FORBIDDEN)
#         data = request.data
#         _mutable = data._mutable
#         data._mutable = True
#         genres = data.get('genre')
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def partial_update(self, request, pk=None):
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     def destroy(self, request, pk=None):
#         if not request.user.is_authenticated:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         if hasattr(request.user, 'role'):
#             if not (request.user.is_superuser or request.user.role == 'admin'):
#                 return Response(status=status.HTTP_403_FORBIDDEN)
#         else:
#             if not request.user.is_superuser:
#                 return Response(status=status.HTTP_403_FORBIDDEN)
#         genres = self.queryset.all()
#         genre = get_object_or_404(genres, slug=pk)
#         genre.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsSuperUserOrAdmin | ReadOnly]
    # filterset_class = TitleFilter

    def check_exists(self):
        category = self.request.data.get('category', None)
        if 'multipart/form-data' in self.request.content_type:
            genre = self.request.data.getlist('genre', None)
        else:
            genre = self.request.data.get('genre', None)

        self.cat_obj = None
        self.gen_obj = []

        if (category is None) or (genre is None):
            exists_status = True

        else:
            try:
                if category:
                    self.cat_obj = Category.objects.get(slug=category)

                if genre:
                    self.gen_obj = Genre.objects.filter(slug__in=genre)

                exists_status = True
            except:
                exists_status = False

            return self.cat_obj, self.gen_obj, exists_status

    def create(self, serializer):
        # if not request.user.is_authenticated:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)

        self.cat_obj, self.gen_obj, exists_status = self.check_exists()

        if exists_status is False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return super(viewsets.ModelViewSet, self).create(self.request, *self.args, **self.kwargs)

    def perform_create(self, serializer):
        serializer.save(category=self.cat_obj, genre=self.gen_obj)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        partial = True
        self.cat_obj, self.gen_obj, exists_status = self.check_exists()

        if exists_status is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save(category=self.cat_obj, genre=self.gen_obj)


# class GenreListCreate(generics.ListCreateAPIView):
#     serializer_class = GenreSerializer
#     queryset = Genre.objects.all()
#     permission_classes = [IsAuthenticated | ReadOnly]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['=name']
