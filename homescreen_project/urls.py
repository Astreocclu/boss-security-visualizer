"""
URL configuration for homescreen_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # Include your app's urls
    # Add Browsable API login/logout views for development
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Serve React frontend
    re_path(r'^$', TemplateView.as_view(template_name='index.html')),
    re_path(r'^(?!admin|api|api-auth|media|static).*$', TemplateView.as_view(template_name='index.html')),
]

# Add media file serving during development ONLY
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
