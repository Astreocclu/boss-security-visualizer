from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .auth_views import (
    CustomTokenObtainPairView,
    DevLoginView,
    CustomTokenRefreshView,
    register_user,
    logout_user,
    user_profile,
    update_profile
)

from .audit.views import AuditViewSet
from .views_config import TenantConfigView

# Create a router and register our viewsets with it.
router = DefaultRouter()

router.register(r'visualizations', views.VisualizationRequestViewSet, basename='visualizationrequest')
router.register(r'generated-images', views.GeneratedImageViewSet, basename='generatedimage')
router.register(r'profile', views.UserProfileViewSet, basename='userprofile')
router.register(r'ai-services', views.AIServiceViewSet, basename='aiservice')
router.register(r'screentypes', views.ScreenTypeViewSet, basename='screentype')
router.register(r'audit', AuditViewSet, basename='audit')
router.register(r'leads', views.LeadViewSet, basename='lead')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # Authentication endpoints
    path('auth/login/', DevLoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', register_user, name='register'),
    path('auth/logout/', logout_user, name='logout'),

    # User profile endpoints
    path('auth/profile/', user_profile, name='user_profile'),
    path('auth/profile/update/', update_profile, name='update_profile'),

    # API endpoints
    path('config/', TenantConfigView.as_view(), name='tenant-config'),
    path('visualization/<int:pk>/pdf/', views.VisualizationRequestViewSet.as_view({'get': 'pdf'}), name='visualization-pdf'),
    path('', include(router.urls)),
]
