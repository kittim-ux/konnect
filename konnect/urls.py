"""konnect URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from konnect_admin import views



#router.register(r'home', homeViewSet, basename='user')
router = routers.DefaultRouter() 
router.register(r'connected_tvs', views.ConnectedTVsDetailView, basename='connected_tvs')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('konnect_admin.urls')),
   # path('api', views.home, name='home'),
]
