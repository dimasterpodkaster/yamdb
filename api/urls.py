from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from api.views import (RegistrationAPIView, LoginAPIView, UserViewSet, PersonalViewSet, CategoryViewSet, GenreViewSet,
                       TitleViewSet)

router = DefaultRouter()
router.register(r'users/me', PersonalViewSet)
router.register('users', UserViewSet)
router.register(r'users/<username>', UserViewSet)
router.register('categories', CategoryViewSet)
router.register(r'categories/<slug>', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register(r'genres/<slug>', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(r'titles/<slug>', TitleViewSet)

urlpatterns = [
        # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/email/', RegistrationAPIView.as_view(), name='token_reg'),
        path('auth/token/', LoginAPIView.as_view(), name='token_log'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('', include(router.urls)),
    ]
