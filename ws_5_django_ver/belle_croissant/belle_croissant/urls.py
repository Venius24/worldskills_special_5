"""
URL Configuration for Belle Croissant Lyonnais
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('promotions/', include('promotions.urls')),
    path('loyalty/', include('loyalty.urls')),
    path('api/', include('api_mock.urls')),
]