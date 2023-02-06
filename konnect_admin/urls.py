from django.urls import path, include
from rest_framework import routers
from . import views
from konnect_admin.views import ConnectedTVsListView, ConnectedTVsDetailView


router = routers.DefaultRouter()

#router.register(r'home', homeViewSet, basename='user')

#The url path for the API
urlpatterns = [
    path('connectedtvs/', ConnectedTVsListView.as_view(), name='connected_tvs'),
    path('connectedtvs/<int:id>/', ConnectedTVsDetailView.as_view(), name='connected_tv_detail'),

]
